# Cleaned data

Run the pipeline from the repository root:

```bash
python -m pip install -r requirements.txt
python src/01_generate_data.py
python src/02_clean_data.py
```

The cleaning script reads, but never overwrites, `data/raw/*.csv`. It writes
the cleaned CSV files to this directory and records issue categories, applied
rules, and affected-row counts in `reports/cleaning_log.csv`.

Cleaning rules preserve valid negative available stock because it can represent
a stock-out. Only an extreme injected value below -1000 is treated as invalid
and reconstructed from opening, received, and issued quantities. Missing
identifiers are not invented: the script stops and reports them.
