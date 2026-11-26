# StockWise automated tests

Run from the repository root:

```bash
python src/01_generate_data.py
python src/02_clean_data.py
python tests/run_tests.py
```

The runner writes `reports/test_results.csv` with PASS, FAIL, and SKIP rows.
The Oracle reconciliation test is skipped until actual CSV exports from the
seven Oracle queries are present in `reports/sql_results/`. A skipped Oracle
check is not a successful SQL reconciliation; run the Oracle loader first.
