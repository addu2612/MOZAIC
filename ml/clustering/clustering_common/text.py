import re
from typing import Dict

IP_RE = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
ISO_TS_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?\b")
HEX_RE = re.compile(r"\b0x[0-9a-fA-F]+\b")
NUM_RE = re.compile(r"\b\d+\.?\d*\b")
PATH_RE = re.compile(r"\b\/[\w\-\./]+\b")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = IP_RE.sub("<ip_address>", text)
    text = UUID_RE.sub("<uuid>", text)
    text = ISO_TS_RE.sub("<timestamp>", text)
    text = HEX_RE.sub("<hex>", text)
    text = PATH_RE.sub("<path>", text)
    text = NUM_RE.sub("<num>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def flatten_metadata(meta: Dict) -> str:
    if not meta:
        return ""
    parts = []
    for k in sorted(meta.keys()):
        parts.append(f"{k}={meta[k]}")
    return " ".join(parts)
