"""MOZAIC Demo API

Purpose: give a working end-to-end demo (frontend -> API -> results) without
requiring DB migrations, saved model weights, or live MCP ingestion.

This reads the pre-generated clustering outputs from /home/arnav/majorproject/
so we can show a working dashboard in a teacher meeting.

Run:
  cd /home/arnav/majorproject/MOZAIC/backend
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn demo_api:app --host 0.0.0.0 --port 8001 --reload
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE = Path("/Users/arnavpanicker/trial")

# Offline research outputs (already present)
GRAFANA_METRICS = BASE / "clustering_grafana" / "output" / "report" / "metrics.json"
GRAFANA_CLUSTERS = BASE / "clustering_grafana" / "output" / "grafana_clusters.json"
K8S_CLUSTERS_SAMPLED = BASE / "clustering_k8s" / "output_sampled" / "k8s_clusters.json"

# Synthetic dataset metadata (Grafana-style) used to derive uptime/time-of-day patterns and error-type distribution.
GRAFANA_METADATA = BASE / "outputs" / "results" / "metadata.csv"
DATASET_SUMMARY = BASE / "outputs" / "results" / "dataset_summary.json"

# Full multi-source synthetic logs (for teacher demo). We will generate into this folder.
SYNTHETICLOGS_ROOT = BASE / "syntheticlogs"
DEMO_OUTPUT_DIR = Path(os.environ.get("MOZAIC_DEMO_OUTPUT_DIR", str(SYNTHETICLOGS_ROOT / "output_demo")))

# Tiny, deterministic mapping for a demo.
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

# Severity mapping (mirrors clustering_common/severity.py for Grafana anomaly types)
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


def _top_cluster_sizes(metrics: Dict[str, Any], top_n: int = 12) -> List[Dict[str, Any]]:
    sizes = metrics.get("cluster_sizes", {})
    items = [(int(k), int(v)) for k, v in sizes.items()]
    items.sort(key=lambda kv: kv[1], reverse=True)

    out: List[Dict[str, Any]] = []
    for cid, size in items[:top_n]:
        error_type = ERROR_TYPES[cid % len(ERROR_TYPES)]
        sev = _severity_for_error_type(error_type)
        out.append(
            {
                "cluster_id": cid,
                "size": size,
                "severity": sev,
                "error_type": error_type,
                "summary": f"Cluster {cid} grouped {size} related events.",
            }
        )
    return out


class SolutionRequest(BaseModel):
    cluster_id: int
    error_type: str
    severity: str


class SetOutputDirRequest(BaseModel):
    path: str


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


app = FastAPI(title="MOZAIC Demo API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/demo/status")
def demo_status() -> Dict[str, Any]:
    return {
        "demo_output_dir": str(DEMO_OUTPUT_DIR),
        "has_demo_incidents": _demo_incidents_path().exists(),
        "sources_present": {
            s: _source_dir(s).exists() for s in ("grafana", "kubernetes", "cloudwatch", "sentry")
        },
    }


@app.post("/demo/set_output_dir")
def demo_set_output_dir(req: SetOutputDirRequest) -> Dict[str, Any]:
    global DEMO_OUTPUT_DIR
    p = Path(req.path).expanduser().resolve()
    DEMO_OUTPUT_DIR = p
    return {"ok": True, "demo_output_dir": str(DEMO_OUTPUT_DIR)}


@app.get("/demo/incidents")
def demo_incidents() -> Dict[str, Any]:
    incidents = _read_incidents()
    # Sort by severity then event_count
    sev_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    incidents.sort(key=lambda x: (sev_rank.get(x.get("severity", "P3"), 9), -int(x.get("event_count", 0))))
    return {"incidents": incidents}


@app.get("/demo/log_samples")
def demo_log_samples(source: str = "grafana", limit: int = 5) -> Dict[str, Any]:
    # Return a few raw log lines to use as evidence in the UI.
    src = source
    # Map UI ids to generator dirs
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


@app.get("/demo/overview")
def demo_overview() -> Dict[str, Any]:
    try:
        metrics = _read_json(GRAFANA_METRICS)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Missing metrics file: {e}")

    core = metrics.get("metrics", {})
    return {
        "source": "grafana",
        "metrics": core,
        "severity_counts": metrics.get("severity_counts", {}),
        "top_clusters": _top_cluster_sizes(metrics, top_n=10),
    }


@app.get("/demo/sources")
def demo_sources() -> Dict[str, Any]:
    # For the teacher demo, expose 4 sources even if only some have full data wired.
    return {
        "sources": [
            {
                "id": "grafana",
                "label": "Grafana",
                "has_clusters": GRAFANA_CLUSTERS.exists(),
                "has_metrics": GRAFANA_METRICS.exists(),
                "has_uptime": GRAFANA_METADATA.exists(),
            },
            {
                "id": "k8s",
                "label": "Kubernetes",
                "has_clusters": K8S_CLUSTERS_SAMPLED.exists(),
            },
            {
                "id": "cloudwatch",
                "label": "CloudWatch",
                "has_clusters": False,
            },
            {
                "id": "sentry",
                "label": "Sentry",
                "has_clusters": False,
            },
        ]
    }


@app.get("/demo/clusters")
def demo_clusters(source: str = "grafana", top_n: int = 15) -> Dict[str, Any]:
    if source != "grafana":
        # Keep it simple for demo
        if source == "k8s":
            if not K8S_CLUSTERS_SAMPLED.exists():
                raise HTTPException(status_code=404, detail="k8s sampled clusters not found")
            data = _read_json(K8S_CLUSTERS_SAMPLED)
            # sampled file may have different schema; just show counts
            labels = data.get("labels", [])
            # compute sizes
            counts: Dict[int, int] = {}
            for cid in labels:
                counts[int(cid)] = counts.get(int(cid), 0) + 1
            items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
            clusters = []
            for cid, size in items:
                et = ERROR_TYPES[cid % len(ERROR_TYPES)]
                sev = _severity_for_error_type(et)
                clusters.append({"cluster_id": cid, "size": size, "severity": sev, "error_type": et})
            return {"source": source, "clusters": clusters}

        # For CloudWatch/Sentry we return placeholder clusters for UI continuity.
        if source in ("cloudwatch", "sentry"):
            try:
                summary = _read_json(DATASET_SUMMARY)
                dist = summary.get("anomaly_distribution", {})
            except Exception:
                dist = {}
            items = list(dist.items())[:top_n]
            clusters = []
            for i, (etype, count) in enumerate(items):
                sev = _severity_for_error_type(etype)
                clusters.append({"cluster_id": i, "size": int(count), "severity": sev, "error_type": etype})
            return {"source": source, "clusters": clusters}

        raise HTTPException(status_code=400, detail="unknown source")

    try:
        metrics = _read_json(GRAFANA_METRICS)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Missing metrics file: {e}")

    return {"source": "grafana", "clusters": _top_cluster_sizes(metrics, top_n=top_n)}


@app.get("/demo/error_types")
def demo_error_types(source: str = "grafana", top_n: int = 8) -> Dict[str, Any]:
    # Return distribution of error/anomaly types for charting.
    try:
        summary = _read_json(DATASET_SUMMARY)
        dist = summary.get("anomaly_distribution", {})
    except Exception:
        dist = {}

    items = [(k, int(v)) for k, v in dist.items()]
    items.sort(key=lambda kv: kv[1], reverse=True)
    out = [{"error_type": k, "count": v, "severity": _severity_for_error_type(k)} for k, v in items[:top_n]]
    return {"source": source, "items": out}


@app.get("/demo/uptime")
def demo_uptime(source: str = "grafana") -> Dict[str, Any]:
    # Compute a simple per-hour uptime curve from synthetic metadata.
    # Uptime = 1 - anomaly_rate for that hour.
    if not GRAFANA_METADATA.exists():
        raise HTTPException(status_code=404, detail="metadata.csv not found")

    import csv
    from datetime import datetime

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
        uptime = 1.0 if t == 0 else max(0.0, 1.0 - (a / t))
        series.append({"hour": h, "uptime": uptime, "total": t, "anomalies": a})

    return {"source": source, "series": series}


@app.post("/demo/solution")
def demo_solution(req: SolutionRequest) -> Dict[str, Any]:
    # This is intentionally deterministic and demo-friendly.
    # In the real system this would call an LLM with retrieved context.
    base_steps = [
        "Confirm the incident scope: which service, region, and time window.",
        "Check correlated signals: error rate, latency, and saturation.",
        "Inspect recent deploys/config changes and roll back if needed.",
        "Add an alert rule + runbook entry to prevent recurrence.",
    ]

    type_steps = {
        "high_error_rate": [
            "Look for top failing endpoints and exception types.",
            "Check downstream dependency health (DB, cache, external API).",
        ],
        "cpu_spike": [
            "Check pod CPU limits/requests and HPA behavior.",
            "Identify hot paths via profiling or slow logs.",
        ],
        "memory_spike": [
            "Check memory leaks and GC pressure (heap usage over time).",
            "Restart the worst offenders if safe, then patch.",
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
