from typing import List, Dict, Any
import re
from sklearn.cluster import HDBSCAN
import numpy as np

async def cluster_logs(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Cluster similar log entries using embeddings"""
    
    if not logs:
        return []
    
    # Simple placeholder-based clustering (replace with LogBERT embeddings)
    texts = []
    for log in logs:
        if isinstance(log['data'], dict):
            text = str(log['data'].get('message', log['data'].get('reason', '')))
        else:
            text = str(log['data'])
        texts.append(preprocess_log(text))
    
    # TODO: Replace with actual embedding model (LogBERT/RoBERTa)
    # For now, use simple feature extraction
    if len(texts) < 2:
        return [{"cluster_id": 0, "logs": logs}]
    
    # Placeholder: group by source for now
    clusters = {}
    for i, log in enumerate(logs):
        source = log['source']
        if source not in clusters:
            clusters[source] = []
        clusters[source].append(log)
    
    return [
        {"cluster_id": i, "source": source, "logs": cluster_logs}
        for i, (source, cluster_logs) in enumerate(clusters.items())
    ]

def preprocess_log(text: str) -> str:
    """Preprocess log text with semantic placeholders"""
    text = re.sub(r'\d+', '<NUM>', text)
    text = re.sub(r'\b[0-9a-f]{8,}\b', '<HEX>', text)
    text = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', text)
    return text.lower()