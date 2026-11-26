# Oracle loading and SQL reports

## Prerequisites

1. Create an Oracle Database schema/user for this project.
2. Run `sql/schema.sql` in that schema.
3. Install the Python packages from the repository root:

```bash
python -m pip install -r requirements.txt
```

4. Set the following environment variables. Do not put credentials in source files.

PowerShell:
```powershell
$env:STOCKWISE_ORACLE_USER="your_username"
$env:STOCKWISE_ORACLE_PASSWORD="your_password"
$env:STOCKWISE_ORACLE_DSN="localhost:1521/your_service"
```

Command Prompt:
```bat
set STOCKWISE_ORACLE_USER=your_username
set STOCKWISE_ORACLE_PASSWORD=your_password
set STOCKWISE_ORACLE_DSN=localhost:1521/your_service
```

## Run the pipeline

```bash
python src/01_generate_data.py
python src/02_clean_data.py
python src/03_load_sql.py --replace
```

Use `--replace` only in the dedicated StockWise schema: it deletes existing
StockWise fact and dimension rows in foreign-key-safe order before reloading.
If the tables are already populated and you only want fresh query CSVs, run:

```bash
python src/03_load_sql.py --skip-load
```

The seven queries are in `sql/queries.sql`. Results are exported to
`reports/sql_results/`. The Oracle procedure in `sql/procedures.sql` returns
the current low-stock and stock-out product list through a SYS_REFCURSOR.

Oracle execution requires an available Oracle instance and valid credentials.
The Python loader can be syntax-checked without Oracle, but query execution
cannot be reported as successful until it has run against the database.
