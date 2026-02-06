# Shared Clustering Utilities

Common utilities for preprocessing, embeddings, clustering, and Ollama labeling.

## Dependencies
- sentence-transformers
- hdbscan
- scikit-learn
- numpy

Install in your venv:
```bash
pip install sentence-transformers hdbscan scikit-learn numpy
```

## External LLM Labeling (Optional)
Use on a sampled cluster output if you want Groq/Gemini labels.

Gemini:
```bash
export GOOGLE_API_KEY=...
python3 clustering_common/label_external_llm.py \
  --input clustering_grafana/output/grafana_clusters.json \
  --output clustering_grafana/output/grafana_clusters_labeled.json \
  --provider gemini \
  --model gemini-1.5-flash
```

Groq:
```bash
export GROQ_API_KEY=...
python3 clustering_common/label_external_llm.py \
  --input clustering_k8s/output/k8s_clusters.json \
  --output clustering_k8s/output/k8s_clusters_labeled.json \
  --provider groq \
  --model grok-2-latest
```

## Cluster Suggestions (Optional)
Generate root-cause guesses and remediation steps from cluster samples using Ollama:
```bash
python3 clustering_common/cluster_suggestions.py \
  --input clustering_k8s/output/k8s_clusters.json \
  --output clustering_k8s/output/k8s_clusters_suggestions.json \
  --ollama_model llama3.2:latest
```
