# Lottery Statistical Forensics Lab

Reproducible statistical analysis of lottery draw histories against stated random models.

## CLI

```bash
forensic simulate --game lotto --runs 1000000
forensic analyze --input draws.csv --game lotto --seed 42 --output reports
```

The lab records dataset/rule hashes, hypotheses, tests, parameters, seed, sample size, multiple-testing correction, and held-out results.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```
