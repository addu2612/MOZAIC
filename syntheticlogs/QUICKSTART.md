# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Extract the package
tar -xzf synthetic-log-generator-complete.tar.gz
cd synthetic-log-generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Validate setup
python validate_setup.py
```

Expected output:
```
✓ All existing files validated successfully!
🎉 Setup validation PASSED!
```

## Generate Your First Dataset (2 minutes)

```bash
# Generate 1 hour of logs
python main.py --hours 1

# Check output
ls -lh output/
```

You should see:
```
output/
├── kubernetes/logs_2024-01-01.jsonl.gz
├── sentry/logs_2024-01-01.jsonl.gz
├── cloudwatch/logs_2024-01-01.jsonl.gz
├── grafana/logs_2024-01-01.jsonl.gz
└── correlation/incidents.json
```

## Verify the Data

```bash
# Count logs
echo "Kubernetes: $(zcat output/kubernetes/*.gz | wc -l) logs"
echo "Sentry: $(zcat output/sentry/*.gz | wc -l) logs"
echo "CloudWatch: $(zcat output/cloudwatch/*.gz | wc -l) logs"
echo "Grafana: $(zcat output/grafana/*.gz | wc -l) logs"

# View sample logs
zcat output/kubernetes/*.gz | head -3 | jq .
zcat output/sentry/*.gz | head -3 | jq .

# Check incidents
cat output/correlation/incidents.json | jq '.incidents | length'
cat output/correlation/incidents.json | jq '.incidents[0]'
```

## Generate Training Data for ML Pipeline

```bash
# 30 days of data (recommended for training)
python main.py --days 30 --output-dir data/training

# 7 days for testing
python main.py --days 7 --output-dir data/testing

# 90 days for comprehensive dataset
python main.py --days 90 --output-dir data/full
```

## Common Use Cases

### High-Volume Testing
```bash
# 1 hour of 10x traffic
python main.py --hours 1 --volume-multiplier 10
```

### Specific Date Range
```bash
# Q1 2024
python main.py --start-date 2024-01-01 --end-date 2024-03-31
```

### Quick Testing (No Compression)
```bash
# Faster for development/testing
python main.py --hours 1 --no-compress
```

## Troubleshooting

**Issue**: Import errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: No output files generated
```bash
# Solution: Check logs, run with verbose
python main.py --hours 1 --verbose
```

**Issue**: Memory error during generation
```bash
# Solution: Generate smaller batches
python main.py --hours 1  # Instead of --days 30
```

## Next Steps

1. **Validate Quality**: See `README.md` for validation methods
2. **Customize**: Edit `config/*.yaml` files
3. **ML Pipeline**: Feed logs into your LogBERT/HDBSCAN pipeline
4. **Iterate**: Adjust patterns based on ML results

## Quick Reference

| Command | Description |
|---------|-------------|
| `python main.py --hours 1` | Generate 1 hour |
| `python main.py --days 7` | Generate 1 week |
| `python main.py --help` | Show all options |
| `python validate_setup.py` | Check installation |

## Support

- **Full Documentation**: `README.md`
- **Configuration**: `config/README.md` (create if needed)
- **Implementation Guide**: `IMPLEMENTATION_COMPLETE.md`
- **Complete Summary**: `COMPLETE_SUMMARY.md`

---

**Ready to go!** Start with `python main.py --hours 1` and scale up from there.
