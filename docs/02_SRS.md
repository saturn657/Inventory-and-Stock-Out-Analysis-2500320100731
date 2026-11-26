# StockWise — Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification defines the functional, non-functional, data, and acceptance requirements for StockWise: Inventory and Stock-Out Analysis. It is intended for the student developer, project evaluator, and anyone reproducing or reviewing the project.

### 1.2 Project Scope

StockWise is an educational data analytics solution for examining inventory availability, stock-out patterns, reorder risks, inventory value, and supplier delivery performance. It uses Python for data generation and preparation, Oracle SQL/PLSQL for relational storage and queries, Excel and Power BI for reporting, and Streamlit for an interactive dashboard.

The initial dataset will be synthetic and reproducible. The system is not intended to connect to a live ERP or to place purchase orders automatically.

### 1.3 Definitions

| Term | Definition |
|---|---|
| SKU | Stock Keeping Unit; a unique identifier for a product |
| Stock-out | A product has available quantity less than or equal to zero |
| Low stock | Available quantity is above zero but at or below its reorder level |
| Reorder level | The configured quantity threshold at which replenishment should be considered |
| Lead time | Number of calendar days between purchase-order date and actual delivery date |
| Fact table | A central analytical table containing measurable business events or quantities |
| Dimension table | A descriptive table used to filter and group fact records |
| KPI | Key Performance Indicator |

## 2. Overall Description

### 2.1 Product Perspective

StockWise is a small, modular analytics pipeline. Python scripts generate, clean, and analyse CSV data. Oracle stores the relational model and supports SQL/PLSQL analysis. The same documented data definitions feed the notebook, Streamlit app, Excel workbook, and Power BI report.

### 2.2 Product Functions

- Generate reproducible raw inventory-related CSV datasets.
- Detect and handle duplicate, missing, invalid, and inconsistent records.
- Record data-quality issues and the rules applied to resolve them.
- Load validated data into an Oracle star schema.
- Run business queries for stock position, stock-outs, inventory value, and supplier performance.
- Produce static charts and a documented analysis notebook.
- Display filtered KPIs and charts in Streamlit.
- Support Excel and Power BI reporting.
- Run automated data-quality and reconciliation tests.

### 2.3 User Classes

| User | Needs |
|---|---|
| Student developer | Generate data, run scripts, debug, and maintain the project |
| Project evaluator / faculty | Review requirements, methods, code, outputs, and test evidence |
| Inventory analyst (demonstration user) | Explore stock levels, low-stock products, stock-outs, and supplier performance |
| Repository user | Reproduce the workflow using documented setup instructions |

### 2.4 Operating Environment

- Windows, macOS, or Linux with a supported Python installation.
- Python 3.10 or later is the intended baseline.
- Oracle Database with a user/schema permitted to create the project tables and run its SQL/PLSQL scripts.
- A modern browser for Streamlit and Power BI Service, where applicable.
- Microsoft Excel for the workbook and Power BI Desktop for creating or editing a PBIX report.
- Git for obtaining the project source.

### 2.5 Assumptions and Dependencies

- The initial dataset is generated locally with a fixed random seed.
- Python packages can be installed from requirements.txt using pip.
- Oracle Database and valid connection credentials are provided by the person running the database loader.
- Credentials are supplied through environment variables or a local, untracked configuration file.
- Excel and Power BI desktop authoring require the relevant Microsoft applications; a PBIX file will only be claimed as delivered if it has actually been created and checked.
- All dashboards and reports use the same documented metric definitions.

### 2.6 Constraints

- The project is designed for a ten-day implementation schedule.
- The initial data is synthetic and does not represent a real organisation.
- No live inventory feed, ERP integration, or automatic purchasing is included.
- Oracle-specific SQL syntax may differ from SQLite, PostgreSQL, or other database systems.
- The project must not commit passwords, API keys, or database credentials.
- Generated results must be traceable to the actual data and scripts.

## 3. Functional Requirements

| ID | Requirement | Verification |
|---|---|---|
| FR1 | The system shall generate reproducible raw CSV datasets using a fixed random seed. | Run the generator twice with the same seed and compare outputs. |
| FR2 | The generated data shall include product, supplier, inventory, purchase-order, and stock-movement information. | Inspect generated CSV files and their documented schemas. |
| FR3 | The raw data shall include controlled examples of duplicates, missing values, invalid values, and inconsistent text. | Run data-quality profiling on raw files. |
| FR4 | The cleaning process shall apply documented rules to identified data-quality issues. | Review cleaning script and quality log. |
| FR5 | The cleaning process shall write validated datasets to the clean-data directory without silently discarding records. | Compare input/output row counts and inspect the issue log. |
| FR6 | The project shall provide a data dictionary based on the actual generated CSV headers. | Compare dictionary fields with CSV headers. |
| FR7 | The project shall define an Oracle-compatible relational schema with primary and foreign keys. | Execute schema script in a configured Oracle schema. |
| FR8 | The project shall load validated records into the Oracle tables. | Check inserted row counts and referential integrity. |
| FR9 | The project shall provide at least seven business SQL queries using joins, grouping, and aggregate functions where appropriate. | Execute queries and inspect saved outputs. |
| FR10 | The project shall calculate stock-out, low-stock, inventory-value, and supplier lead-time measures using documented rules. | Recalculate selected records independently and compare. |
| FR11 | The project shall generate at least five static analytical chart files. | Run chart script and confirm output files. |
| FR12 | The notebook shall explain each analysis stage with Markdown and show insights derived from actual data. | Review notebook cells and reproduce execution. |
| FR13 | The Streamlit app shall provide at least four KPI tiles, sidebar filters, and at least three interactive charts. | Run the app and interact with each filter. |
| FR14 | The project shall provide Power BI model and report instructions, including DAX measures and three report pages. | Review documentation and verify the PBIX if created. |
| FR15 | The project shall provide an Excel workbook with documented cleaning, analysis, and dashboard components. | Open workbook and inspect sheets, formulas, and pivots. |
| FR16 | Automated tests shall check data quality, relationships, and Python/SQL reconciliation where Oracle execution is available. | Run test suite and inspect PASS/FAIL output. |
| FR17 | The README shall document installation, execution order, data source, assumptions, and known limitations. | Follow the README from a clean checkout. |

## 4. Non-Functional Requirements

| ID | Requirement | Measurable acceptance target |
|---|---|---|
| NFR1 — Reproducibility | Data generation and analysis shall be repeatable. | Fixed-seed generation produces identical CSV content in repeated runs. |
| NFR2 — Data integrity | Required identifiers and relationships shall remain valid after cleaning. | No duplicate primary keys, missing required keys, or orphan foreign keys in clean data. |
| NFR3 — Traceability | Cleaning decisions shall be recorded. | Each detected issue category has a rule and affected-row count in the quality log. |
| NFR4 — Correctness | Core metrics shall use one shared definition across outputs. | Python and Oracle totals match for the same loaded dataset, subject to documented numeric precision. |
| NFR5 — Usability | A new user shall be able to set up the Python workflow from documentation. | Setup and data pipeline can be run by following the README commands without editing source code. |
| NFR6 — Maintainability | Scripts and SQL shall be separated by responsibility. | Generation, cleaning, loading, analysis, app, and tests are in their documented files. |
| NFR7 — Security | Credentials shall not be stored in tracked source files. | Repository scan finds no real credentials; local environment configuration is ignored by Git. |
| NFR8 — Portability | The Python workflow shall support common desktop operating systems. | Paths are handled with pathlib and no hard-coded machine-specific absolute paths are required. |
| NFR9 — Performance | The educational dataset shall process on a typical student laptop. | The full Python generation, cleaning, and chart pipeline completes within 2 minutes for the documented dataset size on the developer's test machine; actual measured time will be recorded. |
| NFR10 — Documentation | Key assumptions and limitations shall be visible. | README, data dictionary, and final report identify synthetic data and metric definitions. |

## 5. Data Requirements

### 5.1 Planned Data Entities

Exact columns and row counts will be finalised from the generated CSV files and recorded in the data dictionary.

| Entity | Purpose | Example attributes |
|---|---|---|
| Product | Describes each inventory item | product_id, SKU, product_name, category, unit_cost, reorder_level, supplier_id |
| Supplier | Describes product suppliers | supplier_id, supplier_name, region |
| Inventory | Stores stock position by product and date/location | inventory_id, product_id, snapshot_date, available_quantity |
| Purchase Order | Records replenishment orders and delivery dates | order_id, supplier_id, product_id, order_date, expected_delivery_date, actual_delivery_date, quantity_ordered |
| Stock Movement | Records inventory increases and decreases | movement_id, product_id, movement_date, movement_type, quantity |

### 5.2 Data Quality Rules

- Primary identifiers must be present and unique in their respective clean tables.
- Required foreign keys must refer to existing parent records.
- Quantities must follow the documented movement convention; impossible or malformed values must be flagged and resolved using an explicit rule.
- Unit cost must be non-negative.
- Reorder level must be non-negative.
- Date fields must parse as valid dates; actual delivery must not precede order date.
- Category, supplier, and movement labels must use a consistent controlled format.
- Missing required identifiers must not be silently fabricated.
- Every correction, exclusion, or unresolved issue must be recorded in the quality log.

### 5.3 Metric Rules

- Stock-out: available quantity <= 0.
- Low stock: 0 < available quantity <= reorder level.
- Inventory value: available quantity multiplied by unit cost.
- Supplier lead time: actual delivery date minus order date, in calendar days.
- Delayed delivery: actual delivery date later than expected delivery date.

## 6. External Interface Requirements

### 6.1 User Interface

The Streamlit interface shall include:
- Sidebar filters for available dimensions such as date, category, product, and supplier, depending on the final dataset.
- Four KPI tiles for key inventory measures.
- At least three interactive charts.
- A visible caption identifying the dataset as synthetic, if synthetic data is used.
- Clear labels, units, and empty-filter handling.

### 6.2 Software Interfaces

- Python scripts read and write CSV files using documented project-relative paths.
- Oracle connectivity uses the official Python Oracle driver and credentials provided outside source control.
- Excel and Power BI consume the documented cleaned CSV outputs or approved database views.
- The notebook and Streamlit app use the same cleaned data and business definitions as the analysis scripts.

### 6.3 Hardware Interfaces

No specialised hardware is required. A standard computer capable of running Python, a browser, and the selected database client is sufficient.

## 7. Acceptance Criteria

The project is accepted when all applicable criteria below are met and evidence is stored in the repository:

1. Project definition, synopsis, and this SRS are present and consistent with the ten-day plan.
2. The fixed-seed generator creates all documented raw datasets.
3. The data dictionary matches the actual CSV schemas.
4. Cleaning produces clean datasets and a quality log with issue categories, applied rules, and affected-row counts.
5. The Oracle schema script defines keys and constraints and executes successfully in a configured Oracle environment.
6. The loader and seven SQL queries execute successfully when Oracle credentials and database access are available; otherwise, the limitation is explicitly recorded and no successful execution is claimed.
7. At least five chart files and an executable analysis notebook are produced from the clean data.
8. The Streamlit app runs and its filters update the displayed metrics and charts.
9. Power BI model/report documentation and Excel workbook are included; a PBIX is marked complete only after it exists and has been validated in Power BI Desktop.
10. Automated tests report their actual PASS/FAIL results, and any environment-dependent tests are clearly identified.
11. README and final report explain how to reproduce the workflow, the data source, assumptions, and limitations.
12. No credentials, fabricated results, or unsupported claims are included in the repository.

## 8. Requirement Traceability

| Requirement group | Main implementation |
|---|---|
| FR1–FR3 | src/01_generate_data.py |
| FR4–FR6 | src/02_clean_data.py and docs/Data_Dictionary.xlsx |
| FR7 | sql/schema.sql and docs/star_schema.png |
| FR8–FR10 | src/03_load_sql.py, sql/queries.sql, and SQL result files |
| FR11–FR12 | src/04_analysis_charts.py and notebooks/Analysis.ipynb |
| FR13 | app/streamlit_app.py |
| FR14 | Power BI documentation and validated PBIX artifact, if available |
| FR15 | Excel workbook and supporting documentation |
| FR16 | tests/test_pipeline.py and reports/test_results.csv |
| FR17 | README.md |
