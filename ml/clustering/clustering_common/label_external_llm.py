import argparse
import importlib.metadata as importlib_metadata
import json
import os
import time
from typing import Dict

try:
    import importlib_metadata as importlib_metadata_backport  # type: ignore
except Exception:  # pragma: no cover - optional
    importlib_metadata_backport = None

if not hasattr(importlib_metadata, "packages_distributions") and importlib_metadata_backport is not None:
    importlib_metadata.packages_distributions = importlib_metadata_backport.packages_distributions  # type: ignore


def label_with_gemini(
    top_terms: Dict[str, list],
    model: str,
    max_retries: int,
    retry_sleep: int,
    per_request_sleep: float,
) -> Dict[str, str]:
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise RuntimeError("google-generativeai not installed") from exc

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    genai.configure(api_key=api_key)
    client = genai.GenerativeModel(model)

    labels: Dict[str, str] = {}
    for cluster_id, terms in top_terms.items():
        prompt = (
            "You are labeling incident clusters. "
            "Given keywords from logs, output a short label (2-5 words).\n\n"
            f"Keywords: {', '.join(terms)}\n"
            "Label:"
        )
        attempt = 0
        while True:
            try:
                resp = client.generate_content(prompt)
                labels[cluster_id] = (resp.text or "").strip()
                break
            except Exception as exc:
                attempt += 1
                if attempt > max_retries:
                    raise
                if "429" in str(exc) or "ResourceExhausted" in str(exc):
                    time.sleep(retry_sleep)
                else:
                    time.sleep(2)
        if per_request_sleep > 0:
            time.sleep(per_request_sleep)
    return labels


def label_with_groq(
    top_terms: Dict[str, list],
    model: str,
    base_url: str,
    max_retries: int,
    retry_sleep: int,
    per_request_sleep: float,
) -> Dict[str, str]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai not installed") from exc

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    client = OpenAI(api_key=api_key, base_url=base_url)

    labels: Dict[str, str] = {}
    for cluster_id, terms in top_terms.items():
        prompt = (
            "You are labeling incident clusters. "
            "Given keywords from logs, output a short label (2-5 words).\n\n"
            f"Keywords: {', '.join(terms)}\n"
            "Label:"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        attempt = 0
        while True:
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                )
                labels[cluster_id] = (resp.choices[0].message.content or "").strip()
                break
            except Exception as exc:
                attempt += 1
                if attempt > max_retries:
                    raise
                if "429" in str(exc) or "rate limit" in str(exc).lower():
                    time.sleep(retry_sleep)
                else:
                    time.sleep(2)
        if per_request_sleep > 0:
            time.sleep(per_request_sleep)
    return labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provider", choices=["gemini", "groq"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--groq_base_url", default="https://api.groq.com/openai/v1")
    parser.add_argument("--max_retries", type=int, default=5)
    parser.add_argument("--retry_sleep", type=int, default=35)
    parser.add_argument("--per_request_sleep", type=float, default=0)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    top_terms = {str(k): v for k, v in data.get("top_terms", {}).items()}

    if args.provider == "gemini":
        labels = label_with_gemini(
            top_terms,
            args.model,
            args.max_retries,
            args.retry_sleep,
            args.per_request_sleep,
        )
    else:
        labels = label_with_groq(
            top_terms,
            args.model,
            args.groq_base_url,
            args.max_retries,
            args.retry_sleep,
            args.per_request_sleep,
        )

    data["external_labels"] = {
        "provider": args.provider,
        "model": args.model,
        "labels": labels,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    main()
