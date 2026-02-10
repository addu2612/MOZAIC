from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BASE = Path("/Users/arnavpanicker/trial")
SYNTHETICLOGS_ROOT = BASE / "syntheticlogs"
DEMO_OUTPUT_DIR = Path(os.environ.get("MOZAIC_DEMO_OUTPUT_DIR", str(SYNTHETICLOGS_ROOT / "output_demo")))

DATASET_SUMMARY = BASE / "outputs" / "results" / "dataset_summary.json"
GRAFANA_METADATA = BASE / "outputs" / "results" / "metadata.csv"

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
            },
            {
                "id": "k8s",
                "label": "Kubernetes",
                "has_logs": _source_dir("kubernetes").exists(),
            },
            {
                "id": "cloudwatch",
                "label": "CloudWatch",
                "has_logs": _source_dir("cloudwatch").exists(),
            },
            {
                "id": "sentry",
                "label": "Sentry",
                "has_logs": _source_dir("sentry").exists(),
            },
        ]
    }


@router.get("/overview")
def overview() -> Dict[str, Any]:
    """High-level metrics for the selected source.

    For Grafana, use existing offline metrics.json if present.
    For others, provide a lightweight overview.
    """
    grafana_metrics = BASE / "clustering_grafana" / "output" / "report" / "metrics.json"
    if grafana_metrics.exists():
        data = _read_json(grafana_metrics)
        return {
            "source": "grafana",
            "metrics": data.get("metrics", {}),
            "severity_counts": data.get("severity_counts", {}),
        }

    return {
        "source": "grafana",
        "metrics": {"num_points": 0, "num_clusters": 0, "num_noise": 0, "silhouette_score": 0.0},
        "severity_counts": {},
    }


@router.get("/clusters")
def clusters(source: str = "grafana", top_n: int = 15) -> Dict[str, Any]:
    """Return cluster-like aggregates for charts/table.

    Grafana: uses offline cluster sizes from metrics.json.
    Kubernetes: uses sampled clusters if present.
    CloudWatch/Sentry: uses anomaly distribution as a placeholder aggregate.
    """

    if source == "k8s":
        source = "kubernetes"

    if source == "grafana":
        grafana_metrics = BASE / "clustering_grafana" / "output" / "report" / "metrics.json"
        if grafana_metrics.exists():
            data = _read_json(grafana_metrics)
            sizes = data.get("cluster_sizes", {})
            items = [(int(k), int(v)) for k, v in sizes.items()]
            items.sort(key=lambda kv: kv[1], reverse=True)
            out = []
            for cid, size in items[:top_n]:
                et = ERROR_TYPES[cid % len(ERROR_TYPES)]
                out.append({"cluster_id": cid, "size": size, "severity": _severity_for_error_type(et), "error_type": et})
            return {"source": "grafana", "clusters": out}
        return {"source": "grafana", "clusters": []}

    if source == "kubernetes":
        k8s_sampled = BASE / "clustering_k8s" / "output_sampled" / "k8s_clusters.json"
        if not k8s_sampled.exists():
            return {"source": "k8s", "clusters": []}
        data = _read_json(k8s_sampled)
        labels = data.get("labels", [])
        counts: Dict[int, int] = {}
        for cid in labels:
            cid = int(cid)
            counts[cid] = counts.get(cid, 0) + 1
        items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
        out = []
        for cid, size in items:
            et = ERROR_TYPES[cid % len(ERROR_TYPES)]
            out.append({"cluster_id": cid, "size": size, "severity": _severity_for_error_type(et), "error_type": et})
        return {"source": "k8s", "clusters": out}

    # Placeholder for cloudwatch/sentry: use dataset anomaly distribution
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
        return {"source": source, "path": None, "samples": []}

    samples = []
    with open(p, "r", encoding="utf-8") as f:
        for _ in range(max(0, limit)):
            line = f.readline()
            if not line:
                break
            samples.append(line.strip())

    return {"source": source, "path": str(p), "samples": samples}


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
        raise HTTPException(status_code=404, detail="metadata.csv not found")

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

    return {
        "cluster_id": req.cluster_id,
        "severity": req.severity,
        "error_type": req.error_type,
        "recommended_actions": type_steps + base_steps,
        "note": "Demo output (rule-based). Replace with RAG + LLM in production.",
    }
