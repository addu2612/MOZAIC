from __future__ import annotations

import csv
import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BASE = Path(os.environ.get("MOZAIC_BASE_DIR", str(PROJECT_ROOT)))
SYNTHETICLOGS_ROOT = BASE / "syntheticlogs"
DEMO_OUTPUT_DIR = Path(os.environ.get("MOZAIC_DEMO_OUTPUT_DIR", str(SYNTHETICLOGS_ROOT / "output_demo")))

DATASET_SUMMARY = BASE / "outputs" / "results" / "dataset_summary.json"
GRAFANA_METADATA = BASE / "outputs" / "results" / "metadata.csv"
GRAFANA_METRICS = BASE / "clustering_grafana" / "output" / "report" / "metrics.json"
K8S_CLUSTERS_SAMPLED = BASE / "clustering_k8s" / "output_sampled" / "k8s_clusters.json"
SENTRY_CLUSTERS_SAMPLED = BASE / "clustering_sentry" / "output_sampled" / "sentry_clusters.json"
SENTRY_METRICS_SAMPLED = BASE / "clustering_sentry" / "output_sampled" / "report" / "metrics.json"
CLOUDWATCH_CLUSTERS_SAMPLED = BASE / "clustering_cloudwatch" / "output_sampled" / "cloudwatch_clusters.json"
CLOUDWATCH_METRICS_SAMPLED = BASE / "clustering_cloudwatch" / "output_sampled" / "report" / "metrics.json"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

ERROR_TYPES = [
    "high_error_rate",
    "cpu_spike",
    "memory_spike",
    "connection_pool_exhaustion",
    "cache_miss_spike",
    "gc_pressure",
    "traffic_spike",
    "slow_response",
]

GRAFANA_SEVERITY = {
    "high_error_rate": "P0",
    "cpu_spike": "P1",
    "memory_spike": "P1",
    "connection_pool_exhaustion": "P0",
    "cache_miss_spike": "P2",
    "gc_pressure": "P2",
    "traffic_spike": "P2",
    "slow_response": "P1",
}


def _severity_for_error_type(error_type: str) -> str:
    if not error_type:
        return "P3"
    return GRAFANA_SEVERITY.get(error_type, "P3")


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _call_gemini_actions(cluster_id: int, error_type: str, severity: str) -> List[str]:
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key not configured")
    prompt = (
        "You are an SRE assistant. Provide exactly 5 concise remediation steps as JSON array of strings.\n"
        f"cluster_id={cluster_id}\n"
        f"error_type={error_type}\n"
        f"severity={severity}\n"
        "Output ONLY JSON array, no markdown."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 300},
    }
    body = json.dumps(payload).encode("utf-8")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )
    if not text:
        raise RuntimeError("Gemini returned empty response")
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()
    actions = json.loads(text)
    if not isinstance(actions, list):
        raise RuntimeError("Gemini response was not a JSON array")
    cleaned = [str(x).strip() for x in actions if str(x).strip()]
    if not cleaned:
        raise RuntimeError("Gemini returned no actions")
    return cleaned[:8]


def _canonical_source(source: str) -> str:
    return "kubernetes" if source == "k8s" else source


def _cluster_file_for_source(source: str) -> Optional[Path]:
    src = _canonical_source(source)
    if src == "kubernetes":
        return K8S_CLUSTERS_SAMPLED
    if src == "sentry":
        return SENTRY_CLUSTERS_SAMPLED
    if src == "cloudwatch":
        return CLOUDWATCH_CLUSTERS_SAMPLED
    return None


def _metrics_file_for_source(source: str) -> Optional[Path]:
    src = _canonical_source(source)
    if src == "grafana":
        return GRAFANA_METRICS
    if src == "sentry":
        return SENTRY_METRICS_SAMPLED
    if src == "cloudwatch":
        return CLOUDWATCH_METRICS_SAMPLED
    return None


def _clusters_from_cluster_json(path: Path, top_n: int = 15) -> List[Dict[str, Any]]:
    data = _read_json(path)
    labels = [int(x) for x in data.get("labels", [])]
    names = data.get("cluster_names", {})
    samples = data.get("cluster_samples", {})

    counts: Dict[int, int] = {}
    for cid in labels:
        counts[cid] = counts.get(cid, 0) + 1

    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    out: List[Dict[str, Any]] = []
    for cid, size in items:
        sev = "P2"
        sample_rows = samples.get(str(cid), [])
        if sample_rows:
            sev = sample_rows[0].get("severity", "P2")
        label = names.get(str(cid), f"cluster_{cid}")
        out.append(
            {
                "cluster_id": cid,
                "size": int(size),
                "severity": sev,
                "error_type": label,
            }
        )
    return out


def _demo_incidents_path() -> Path:
    return DEMO_OUTPUT_DIR / "correlation" / "incidents.json"


def _source_dir(source: str) -> Path:
    return DEMO_OUTPUT_DIR / source


def _pick_first_jsonl(source: str) -> Optional[Path]:
    d = _source_dir(source)
    if not d.exists():
        return None
    files = sorted([p for p in d.glob("*.jsonl") if p.is_file()])
    return files[0] if files else None


def _find_any_jsonl() -> Optional[Path]:
    candidates = [
        BASE / "clustering_sentry" / "output_sampled",
        BASE / "clustering_cloudwatch" / "output_sampled",
        BASE / "clustering_k8s" / "output_sampled",
        BASE / "clustering_grafana" / "output",
    ]
    for d in candidates:
        if not d.exists():
            continue
        files = sorted([p for p in d.rglob("*.jsonl") if p.is_file()])
        if files:
            return files[0]
    return None


def _read_incidents() -> List[Dict[str, Any]]:
    p = _demo_incidents_path()
    if p.exists():
        data = _read_json(p)
        return data.get("incidents", [])

    # Fallback: derive pseudo-incidents from anomaly distribution.
    try:
        summary = _read_json(DATASET_SUMMARY)
        dist = summary.get("anomaly_distribution", {})
    except Exception:
        dist = {}

    items = [(k, int(v)) for k, v in dist.items()]
    items.sort(key=lambda kv: kv[1], reverse=True)
    out = []
    for i, (etype, count) in enumerate(items[:6]):
        out.append(
            {
                "incident_id": f"demo_inc_{i}",
                "incident_type": etype,
                "start_time": "2024-01-01T00:00:00",
                "end_time": "2024-01-01T00:30:00",
                "severity": _severity_for_error_type(etype),
                "affected_services": ["api-gateway"],
                "correlation_id": f"demo_corr_{i}",
                "event_count": count,
            }
        )
    return out


class SetOutputDirRequest(BaseModel):
    path: str


class SolutionRequest(BaseModel):
    cluster_id: int
    error_type: str
    severity: str


class IncidentAssistantRequest(BaseModel):
    incident_id: str
    question: str
    source: Optional[str] = "grafana"


@router.get("/status")
def status() -> Dict[str, Any]:
    return {
        "demo_output_dir": str(DEMO_OUTPUT_DIR),
        "has_demo_incidents": _demo_incidents_path().exists(),
        "sources_present": {
            s: _source_dir(s).exists() for s in ("grafana", "kubernetes", "cloudwatch", "sentry")
        },
    }


@router.post("/set_output_dir")
def set_output_dir(req: SetOutputDirRequest) -> Dict[str, Any]:
    global DEMO_OUTPUT_DIR
    p = Path(req.path).expanduser().resolve()
    DEMO_OUTPUT_DIR = p
    return {"ok": True, "demo_output_dir": str(DEMO_OUTPUT_DIR)}


@router.get("/sources")
def sources() -> Dict[str, Any]:
    return {
        "sources": [
            {
                "id": "grafana",
                "label": "Grafana",
                "has_logs": _source_dir("grafana").exists(),
                "has_clusters": GRAFANA_METRICS.exists(),
            },
            {
                "id": "k8s",
                "label": "Kubernetes",
                "has_logs": _source_dir("kubernetes").exists(),
                "has_clusters": K8S_CLUSTERS_SAMPLED.exists(),
            },
            {
                "id": "cloudwatch",
                "label": "CloudWatch",
                "has_logs": _source_dir("cloudwatch").exists(),
                "has_clusters": CLOUDWATCH_CLUSTERS_SAMPLED.exists(),
            },
            {
                "id": "sentry",
                "label": "Sentry",
                "has_logs": _source_dir("sentry").exists(),
                "has_clusters": SENTRY_CLUSTERS_SAMPLED.exists(),
            },
        ]
    }


@router.get("/overview")
def overview(source: str = "grafana") -> Dict[str, Any]:
    """High-level metrics for the selected source."""
    src = _canonical_source(source)
    metrics_path = _metrics_file_for_source(src)
    if metrics_path and metrics_path.exists():
        data = _read_json(metrics_path)
        return {
            "source": source,
            "metrics": data.get("metrics", {}),
            "severity_counts": data.get("severity_counts", {}),
        }

    clusters_path = _cluster_file_for_source(src)
    if clusters_path and clusters_path.exists():
        labels = [int(x) for x in _read_json(clusters_path).get("labels", [])]
        num_noise = sum(1 for x in labels if x == -1)
        num_clusters = len({x for x in labels if x != -1})
        return {
            "source": source,
            "metrics": {
                "num_points": len(labels),
                "num_clusters": num_clusters,
                "num_noise": num_noise,
                "silhouette_score": None,
            },
            "severity_counts": {},
        }

    return {
        "source": source,
        "metrics": {"num_points": 0, "num_clusters": 0, "num_noise": 0, "silhouette_score": 0.0},
        "severity_counts": {},
    }


@router.get("/clusters")
def clusters(source: str = "grafana", top_n: int = 15) -> Dict[str, Any]:
    """Return cluster aggregates for charts/table."""

    source = _canonical_source(source)

    if source == "grafana":
        if GRAFANA_METRICS.exists():
            data = _read_json(GRAFANA_METRICS)
            sizes = data.get("cluster_sizes", {})
            items = [(int(k), int(v)) for k, v in sizes.items()]
            items.sort(key=lambda kv: kv[1], reverse=True)
            out = []
            for cid, size in items[:top_n]:
                et = ERROR_TYPES[cid % len(ERROR_TYPES)]
                out.append({"cluster_id": cid, "size": size, "severity": _severity_for_error_type(et), "error_type": et})
            return {"source": "grafana", "clusters": out}
        return {"source": "grafana", "clusters": []}

    cluster_file = _cluster_file_for_source(source)
    if cluster_file and cluster_file.exists():
        out = _clusters_from_cluster_json(cluster_file, top_n=top_n)
        # Preserve frontend's existing "k8s" source id for tab matching.
        source_id = "k8s" if source == "kubernetes" else source
        return {"source": source_id, "clusters": out}

    # Fallback aggregate from dataset summary when explicit cluster files are unavailable.
    try:
        summary = _read_json(DATASET_SUMMARY)
        dist = summary.get("anomaly_distribution", {})
    except Exception:
        dist = {}

    items = [(k, int(v)) for k, v in dist.items()]
    items.sort(key=lambda kv: kv[1], reverse=True)
    out = []
    for i, (etype, count) in enumerate(items[:top_n]):
        out.append({"cluster_id": i, "size": count, "severity": _severity_for_error_type(etype), "error_type": etype})
    return {"source": source, "clusters": out}


@router.get("/incidents")
def incidents() -> Dict[str, Any]:
    xs = _read_incidents()
    sev_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    xs.sort(key=lambda x: (sev_rank.get(x.get("severity", "P3"), 9), -int(x.get("event_count", 0))))
    return {"incidents": xs}


@router.get("/log_samples")
def log_samples(source: str = "grafana", limit: int = 5) -> Dict[str, Any]:
    src = source
    if src == "k8s":
        src = "kubernetes"

    p = _pick_first_jsonl(src)
    if p is None:
        # Fallback: derive simple samples from incidents when no jsonl logs exist.
        incidents = _read_incidents()
        samples = []
        for inc in incidents[:max(0, limit)]:
            samples.append(
                f"{inc.get('start_time', '')} | {inc.get('incident_type', 'unknown')} | "
                f"sev={inc.get('severity', 'P3')} | events={inc.get('event_count', 0)}"
            )
        return {"source": source, "path": None, "samples": samples}

    samples = []
    with open(p, "r", encoding="utf-8") as f:
        for _ in range(max(0, limit)):
            line = f.readline()
            if not line:
                break
            samples.append(line.strip())

    return {"source": source, "path": str(p), "samples": samples}


@router.get("/incident_events")
def incident_events(incident_id: str, source: str = "grafana", limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    incidents = _read_incidents()
    incident = next((x for x in incidents if x.get("incident_id") == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail="incident not found")

    src = source
    if src == "k8s":
        src = "kubernetes"

    p = _pick_first_jsonl(src)
    used_fallback = False
    if p is None:
        p = _find_any_jsonl()
        used_fallback = p is not None
    if p is None:
        return {"incident_id": incident_id, "source": source, "events": [], "total": 0, "detail": "no log file"}

    def _parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                return dt.astimezone(tz=None).replace(tzinfo=None)
            return dt
        except Exception:
            return None

    start_dt = _parse_dt(incident.get("start_time"))
    end_dt = _parse_dt(incident.get("end_time"))
    affected = incident.get("affected_services") or []
    include_all = isinstance(affected, list) and "all" in affected

    events: List[Dict[str, Any]] = []
    total = 0
    event_total = int(incident.get("event_count") or 0)
    if event_total <= 0:
        event_total = max(0, limit)
    event_target = min(event_total, max(0, limit))
    skipped = 0
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue

            if not used_fallback:
                ts = obj.get("timestamp") or obj.get("time")
                dt = _parse_dt(ts)
                if start_dt and end_dt and dt:
                    if dt < start_dt or dt > end_dt:
                        continue

                svc = obj.get("service") or obj.get("component") or obj.get("app") or obj.get("source")
                if not include_all and affected and svc and svc not in affected:
                    continue

            total += 1
            if skipped < max(0, offset):
                skipped += 1
                continue
            if len(events) < event_target:
                events.append(obj)
            if len(events) >= event_target:
                break

    if event_total > 0:
        total = event_total
    return {
        "incident_id": incident_id,
        "source": source,
        "events": events,
        "total": total,
        "detail": "fallback log file" if used_fallback else "ok",
        "log_source": p.name if p is not None else None,
        "fallback": used_fallback,
        "offset": offset,
        "limit": limit,
    }


@router.post("/incident_assistant")
def incident_assistant(req: IncidentAssistantRequest) -> Dict[str, Any]:
    incidents = _read_incidents()
    inc = next((x for x in incidents if x.get("incident_id") == req.incident_id), None)
    if inc is None:
        raise HTTPException(status_code=404, detail="incident not found")

    sev = _severity_for_error_type(inc.get("incident_type", ""))
    event_count = int(inc.get("event_count") or 0)
    affected = inc.get("affected_services") or []
    start_time = inc.get("start_time")
    end_time = inc.get("end_time")

    summary = (
        f"Incident {inc.get('incident_id')} is a {inc.get('incident_type')} issue. "
        f"Severity {inc.get('severity') or sev}, {event_count} events, "
        f"time window {start_time} → {end_time}."
    )

    answer = summary
    if req.question:
        q = req.question.lower()
        if "root" in q or "cause" in q:
            answer = f"Likely cause: {inc.get('incident_type')}. Affected services: {', '.join(affected) or 'unknown'}."
        elif "impact" in q or "services" in q:
            answer = f"Impact: {', '.join(affected) or 'unknown'}. Total events: {event_count}."
        elif "time" in q or "when" in q or "duration" in q:
            answer = f"Window: {start_time} → {end_time}."
        else:
            answer = summary

    suggestions = [
        "What is the root cause?",
        "Which services are impacted?",
        "When did it start and end?",
        "How many events were recorded?",
    ]

    return {
        "incident_id": req.incident_id,
        "answer": answer,
        "summary": summary,
        "suggestions": suggestions,
    }


@router.get("/error_types")
def error_types(source: str = "grafana", top_n: int = 8) -> Dict[str, Any]:
    try:
        summary = _read_json(DATASET_SUMMARY)
        dist = summary.get("anomaly_distribution", {})
    except Exception:
        dist = {}

    items = [(k, int(v)) for k, v in dist.items()]
    items.sort(key=lambda kv: kv[1], reverse=True)
    out = [{"error_type": k, "count": v, "severity": _severity_for_error_type(k)} for k, v in items[:top_n]]
    return {"source": source, "items": out}


@router.get("/uptime")
def uptime(source: str = "grafana") -> Dict[str, Any]:
    # Uses existing metadata.csv (Grafana-style) to compute 1 - anomaly rate per hour.
    if not GRAFANA_METADATA.exists():
        return {
            "source": source,
            "series": [],
            "detail": "metadata.csv not found",
        }

    totals = {h: 0 for h in range(24)}
    anomalies = {h: 0 for h in range(24)}

    with open(GRAFANA_METADATA, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            ts = row.get("timestamp")
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts)
            except Exception:
                continue
            h = int(dt.hour)
            totals[h] += 1
            is_anom = (row.get("is_anomaly") or "").strip().lower() in ("true", "1", "yes")
            if is_anom:
                anomalies[h] += 1

    series = []
    for h in range(24):
        t = totals[h]
        a = anomalies[h]
        up = 1.0 if t == 0 else max(0.0, 1.0 - (a / t))
        series.append({"hour": h, "uptime": up, "total": t, "anomalies": a})

    return {"source": source, "series": series}


@router.post("/solution")
def solution(req: SolutionRequest) -> Dict[str, Any]:
    base_steps = [
        "Confirm the incident scope: which service, region, and time window.",
        "Check correlated signals: error rate, latency, and saturation.",
        "Inspect recent deploys/config changes and roll back if needed.",
        "Add an alert rule and runbook entry to prevent recurrence.",
    ]

    type_steps = {
        "high_error_rate": [
            "Look for top failing endpoints and exception types.",
            "Check downstream dependency health (DB, cache, external API).",
        ],
        "cpu_spike": [
            "Check pod CPU limits/requests and autoscaling behavior.",
            "Identify hot paths via profiling or slow logs.",
        ],
        "memory_spike": [
            "Check memory leaks and GC pressure (heap usage over time).",
            "Restart worst offenders if safe, then patch.",
        ],
        "connection_pool_exhaustion": [
            "Increase pool size temporarily and check DB max connections.",
            "Audit connection leaks and timeout settings.",
        ],
        "slow_response": [
            "Check p95/p99 latency and the slowest endpoints.",
            "Investigate N+1 queries, cache misses, and timeouts.",
        ],
    }.get(req.error_type, [])

    fallback_actions = type_steps + base_steps
    note = "Generated from local remediation policy."
    actions = fallback_actions
    try:
        actions = _call_gemini_actions(req.cluster_id, req.error_type, req.severity)
        note = f"Generated by {GEMINI_MODEL}."
    except (RuntimeError, urllib.error.URLError, json.JSONDecodeError):
        pass

    return {
        "cluster_id": req.cluster_id,
        "severity": req.severity,
        "error_type": req.error_type,
        "recommended_actions": actions,
        "note": note,
    }