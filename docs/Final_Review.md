# StockWise — Final Repository Review (P20)

**Review date:** 26 November 2026  
**Repository:** `saturn657/Inventory-and-Stock-Out-Analysis-2500320100731`

## 1. Overall status

The repository contains the project definition, synopsis, SRS, synthetic-data generator, cleaning pipeline, Oracle schema and query code, Python analysis scripts, Streamlit app, notebook, Excel workbook generator, Power BI design documentation, tests, final report, and README.

The core Python data workflow has been run locally after the final cleaning-rule correction. Some platform-dependent deliverables remain pending and are listed explicitly below. No missing binary or database result is being represented by a placeholder.

## 2. Deliverable audit

| Deliverable | Repository status | Review result |
|---|---|---|
| P1 Project definition | Present | Problem, objectives, business questions, rules, scope, ten-day plan |
| P2 Synopsis | Present | Scope, source, tools, deliverables, ten-day plan |
| P3 SRS | Present | Functional/non-functional requirements, data requirements, acceptance criteria |
| P4 Data generator | Present | Fixed seed 42; creates five raw CSV datasets |
| P5 Data dictionary | Present | `docs/Data_Dictionary.xlsx` is present |
| P6 Cleaning pipeline | Present | Cleaning rules, separate clean outputs, quality log |
| P7 Oracle schema and ER diagram | Present | Six tables, constraints, SVG diagram and notes |
| P8 Oracle loader and queries | Present | Python loader, seven SQL queries, PL/SQL procedure |
| P9 Python charts | Present as generator | Script creates seven PNG files locally |
| P10 Jupyter notebook | Present | Notebook JSON checked; full notebook executed locally without cell errors |
| P11 Streamlit app | Present | Code and filter/data helpers checked; browser launch not verified here |
| P12 Power BI data model | Present | Import, date table, relationships and DAX guide |
| P13 Three-page Power BI design | Present as documentation | Three page layouts, DAX additions and PBIX checklist |
| P14 Excel analysis | Generator and guide present | Workbook generated and reopened locally; native PivotTables/slicers remain manual |
| P15 Automated tests | Present | Six PASS, zero FAIL, one SKIP |
| P16 README | Present | Setup, results, assumptions, disclosure, demo status |
| P17 Final report | Present | Results, methods, insights, limitations, conclusion, references |
| P18 Code/viva preparation | Present | Code walkthrough and ten sample viva questions |
| P19 Debugging | Awaiting issue | No specific user-supplied failing command/error/code was available; no speculative fixes |
| P20 Final review | Present | This checklist |

## 3. Local execution and test evidence

The following were run locally after the movement-label correction:

- Synthetic data generation.
- Data cleaning and quality-log creation.
- Seven Python chart outputs.
- Jupyter notebook execution.
- Excel workbook generation and reopening.
- Streamlit data preparation/filter helper checks and Python compilation.
- Automated pytest suite.

Latest automated test report:

| Status | Count |
|---|---:|
| PASS | 6 |
| FAIL | 0 |
| SKIP | 1 |

The skipped test is Python-versus-Oracle reconciliation. It requires real Oracle query-export CSVs.

## 4. Exact items not present in the GitHub repository

These are generated outputs or environment-dependent artifacts. Their generator/source is present, but the outputs are not currently tracked in GitHub:

1. **Raw CSV files:** `data/raw/` contains a placeholder only. Run `python src/01_generate_data.py` to create the five raw CSVs.
2. **Clean CSV files:** `data/clean/` contains a placeholder and instructions only. Run `python src/02_clean_data.py` after data generation.
3. **Chart PNGs:** `reports/charts/` contains a placeholder and instructions only. Run `python src/04_analysis_charts.py` to create the seven charts.
4. **Oracle query result CSVs:** `reports/sql_results/` contains instructions only. Oracle schema execution, data loading, and query export remain pending a configured Oracle instance.
5. **Power BI PBIX:** `powerbi/StockWise.pbix` is not present. Power BI Desktop is required to build, save, reopen, and validate it.
6. **Excel analysis workbook in GitHub:** `excel/StockWise_Analysis.xlsx` is not tracked in the repository. It was generated and validated locally in the current work session; `src/05_build_excel.py` can regenerate it. Native PivotTables and slicers must be added in Excel Desktop.

## 5. Platform checks not completed

- **Oracle:** SQL and PL/SQL source is present, but no Oracle database connection was available. Do not describe the queries as executed or reconciled.
- **Power BI:** data-model, DAX, and three-page design documentation is present, but the PBIX has not been created or validated in Power BI Desktop.
- **Excel:** the workbook generator was run and the workbook reopened successfully. Native PivotTables, slicers, and timelines still require Excel Desktop.
- **Streamlit:** source compilation and data/filter helper checks passed. A live browser session was not launched in this environment.
- **Demo deployment:** no hosted demo URL exists yet.

## 6. Data integrity and claims review

- Synthetic data is labelled as synthetic in the README, notebook, dashboard, and report.
- Results are calculated from the cleaned dataset; no real-company claims are made.
- Stock-out is defined as available quantity <= 0.
- Low stock is defined as 0 < available quantity <= reorder level.
- Inventory value is available quantity × unit cost.
- Supplier lead time and delayed-delivery rules are documented.
- Negative available quantity is retained when it represents a stock-out; the extreme injected sentinel is repaired.
- The cleaning log records the affected rows and correction rules.
- Oracle values are left pending rather than invented.
- PBIX and Excel Desktop completion are not claimed.
- `.gitignore` now excludes local environments, caches, and common credential files.

## 7. Final action list before external submission

- [ ] Clone the repository on the target machine and follow README setup.
- [ ] Generate raw and clean CSVs and verify the cleaning log.
- [ ] Run chart generation and keep the seven PNGs with the final report if required.
- [ ] Configure Oracle, execute schema, load data, run all seven queries, and save outputs.
- [ ] Rerun tests so Oracle reconciliation changes from SKIP to PASS or FAIL based on actual results.
- [ ] Open the Excel workbook in Excel Desktop; create PivotTables, slicers, and timelines; save the completed workbook.
- [ ] Build and validate the three-page PBIX in Power BI Desktop.
- [ ] Launch the Streamlit app in a browser and test all filters and charts.
- [ ] Deploy a demo only if hosting is available, then add the real URL to README.
- [ ] Re-run the final review after these environment-dependent tasks are completed.

## 8. Final assessment

**Core source code and documentation are in place.** The reproducible Python pipeline, notebook, Excel generator, test suite, SQL source, dashboard source, and project documentation have been created. The repository is not yet a fully verified end-to-end submission because Oracle execution, PBIX creation, Excel PivotTables/slicers, and live Streamlit/browser checks remain outstanding.
