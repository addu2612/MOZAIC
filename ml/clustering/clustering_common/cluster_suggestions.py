import argparse
import json
import urllib.request
from typing import Dict, List


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


def build_prompt(cluster_id: int, terms: List[str], samples: List[Dict]) -> str:
    sample_lines = []
    for s in samples:
        msg = s.get("message") or s.get("query") or ""
        sample_lines.append(f"- {msg}")
    sample_text = "\n".join(sample_lines[:5])

    return (
        "You are an incident assistant. "
        "Given a cluster of similar logs, provide: "
        "1) likely root cause in one sentence, "
        "2) 2-4 remediation steps.\n\n"
        f"Cluster ID: {cluster_id}\n"
        f"Keywords: {', '.join(terms)}\n"
        f"Sample logs:\n{sample_text}\n\n"
        "Return in this format:\n"
        "RootCause: ...\n"
        "Steps: 1) ... 2) ... 3) ..."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ollama_model", default="llama3.2:latest")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    top_terms = {int(k): v for k, v in data.get("top_terms", {}).items()}
    samples = {int(k): v for k, v in data.get("cluster_samples", {}).items()}

    suggestions = {}
    for cluster_id, terms in top_terms.items():
        prompt = build_prompt(cluster_id, terms, samples.get(cluster_id, []))
        suggestions[cluster_id] = _ollama_generate(args.ollama_model, prompt)

    data["suggestions"] = {
        "model": args.ollama_model,
        "items": suggestions,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    main()
