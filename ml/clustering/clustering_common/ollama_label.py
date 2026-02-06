import json
import urllib.request
from typing import Dict, List

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover - optional
    tqdm = None

def _ollama_generate(model: str, prompt: str) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "").strip()


def label_clusters(top_terms: Dict[int, List[str]], model: str) -> Dict[int, str]:
    labels: Dict[int, str] = {}
    items = list(top_terms.items())
    if tqdm is not None:
        items = tqdm(items, desc="Ollama labeling")
    for cluster_id, terms in items:
        prompt = (
            "You are labeling incident clusters. "
            "Given keywords from logs, output a short label (2-5 words).\n\n"
            f"Keywords: {', '.join(terms)}\n"
            "Label:"
        )
        labels[cluster_id] = _ollama_generate(model, prompt)
    return labels
