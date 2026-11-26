# StockWise Excel deliverable

Generate the workbook from the cleaned CSV files:

```bash
python -m pip install -r requirements.txt
python src/01_generate_data.py
python src/02_clean_data.py
python src/05_build_excel.py
```

Output: `excel/StockWise_Analysis.xlsx`.

The workbook includes five source data sheets, a product-level stock analysis
sheet, category and supplier summaries, a dashboard with KPI formulas and
three charts, a Python-versus-Oracle cross-check sheet, and instructions.

The Python totals are populated. Oracle SQL totals remain blank and marked
PENDING until the Oracle queries have been executed. The workbook includes
formula-based summaries; native Excel PivotTables and slicers must be added
in Excel Desktop using `Power_Query_Guide.md`.
