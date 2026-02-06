# Kubernetes Clustering Pipeline

This pipeline filters ERROR logs, normalizes log text, embeds with Sentence-BERT, clusters with HDBSCAN, and optionally labels clusters using Ollama.

## Inputs
- `k8s_logs_2023-02-01.jsonl` in repo root

## Run
```bash
python3 run_pipeline.py \
  --input ../k8s_logs_2023-02-01.jsonl \
  --output_dir output \
  --label_with_ollama \
  --ollama_model llama3.2:3b
```

## Context Window
Preserve prior log lines from the same component+namespace:
```bash
python3 run_pipeline.py \
  --input ../k8s_logs_2023-02-01.jsonl \
  --output_dir output_context \
  --context_lines 50 \
  --context_scope component_namespace
```

## Sampling
```bash
python3 run_pipeline.py \
  --input ../k8s_logs_2023-02-01.jsonl \
  --output_dir output \
  --sample_size 2000 \
  --sample_seed 42
```

## Outputs
- `output/k8s_preprocessed.jsonl`
- `output/k8s_embeddings.npy`
- `output/k8s_clusters.json`

## Notes
- Default log level is `ERROR`. Change with `--level`.
