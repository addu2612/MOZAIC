# Grafana Clustering Pipeline

This pipeline filters anomalies, normalizes log text, embeds with Sentence-BERT, clusters with HDBSCAN, and optionally labels clusters using Ollama.

## Inputs
- `grafana.jsonl` in repo root

## Run
```bash
python3 run_pipeline.py \
  --input ../grafana.jsonl \
  --output_dir output \
  --label_with_ollama \
  --ollama_model llama3.2:3b
```

## Context Window
Preserve prior data points for the same dashboard/panel/service:
```bash
python3 run_pipeline.py \
  --input ../grafana.jsonl \
  --output_dir output_context \
  --context_points 20
```

## Sampling
```bash
python3 run_pipeline.py \
  --input ../grafana.jsonl \
  --output_dir output \
  --sample_size 2000 \
  --sample_seed 42
```

## Outputs
- `output/grafana_preprocessed.jsonl`
- `output/grafana_embeddings.npy`
- `output/grafana_clusters.json`

## Notes
- By default, only anomaly logs (`is_anomaly == true`) are clustered.
- Add a small normal sample if you want separation testing:
```bash
python3 run_pipeline.py --input ../grafana.jsonl --include_normal_sample 1000
```
