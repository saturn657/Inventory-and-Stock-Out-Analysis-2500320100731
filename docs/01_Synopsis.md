# StockWise — Project Synopsis

## 1. Project Title

**StockWise: Inventory and Stock-Out Analysis**

## 2. Introduction and Problem Statement

Retail and distribution businesses need to keep sufficient stock available while avoiding unnecessary overstocking. Inconsistent or disconnected product, supplier, inventory, and replenishment records make it difficult to identify stock-out risks, low-stock products, inventory value, and supplier delays.

StockWise is a data analytics project that organises inventory-related data and analyses it using Python, Oracle SQL/PLSQL, Excel, Streamlit, and Power BI. The project will produce measurable insights and interactive reports to support inventory monitoring and replenishment decisions.

## 3. Objectives

1. Generate or source structured product, supplier, inventory, purchase-order, and stock-movement data, then profile and clean it with a documented quality log.
2. Calculate available stock, inventory value, low-stock products, and stock-out products using clearly defined business rules.
3. Measure supplier lead times and identify delayed deliveries using order, expected-delivery, and actual-delivery dates.
4. Build Python, Oracle SQL/PLSQL, Excel, Streamlit, and Power BI outputs and validate important totals across the workflow.

## 4. Scope

### Included
- Dataset design and reproducible data generation, or a documented public data source if a suitable licensed dataset is selected.
- Data profiling, cleaning, transformation, and quality checks using Python and Pandas.
- A relational star schema implemented for Oracle Database.
- SQL queries and PL/SQL logic for inventory and supplier analysis.
- Exploratory analysis, static charts, and a Jupyter notebook.
- An interactive Streamlit dashboard.
- An Excel workbook with cleaned data, pivot-based analysis, and dashboard elements.
- A Power BI data model with DAX measures and three report pages.
- Automated tests and a final project report.

### Excluded
- Live ERP/POS integration and real-time synchronisation.
- Automatic purchase-order creation or supplier communication.
- Production-grade deployment.
- Predictive machine learning or AI recommendations.

## 5. Data Source and Dataset Plan

The initial implementation will use a **reproducible synthetic teaching dataset** generated with Python and a fixed random seed. This makes the project repeatable and allows controlled examples of common data-quality problems such as duplicate records, missing values, invalid quantities, and inconsistent text labels.

The dataset will represent products, suppliers, inventory snapshots, purchase orders, and stock movements. Exact table names, columns, data types, and row counts will be documented after the generator is implemented. Synthetic data will be labelled clearly in the repository, notebook, dashboards, and final report; it will not be presented as real company data.

If a suitable public dataset is adopted later, its original source, licence, access date, and any transformations will be documented before it is used.

## 6. Tools and Technologies

| Tool / Technology | Purpose |
|---|---|
| Python | Data generation, cleaning, analysis, automation, and testing |
| Pandas and NumPy | Tabular processing, transformations, and calculations |
| Matplotlib | Static data visualisations |
| Jupyter Notebook | Step-by-step analysis and documented findings |
| Oracle SQL | Relational schema, joins, aggregations, and business queries |
| Oracle PL/SQL | Database-side procedural logic |
| Streamlit | Interactive web dashboard |
| Microsoft Excel | Power Query, pivot tables, formulas, and dashboard |
| Power BI | Data modelling, DAX measures, and interactive reports |
| Git and GitHub | Version control and project documentation |

Python dependencies will be declared in requirements.txt. Users will install them with python -m pip install -r requirements.txt. Oracle Database access will require a separately configured database and connection details; credentials will be kept outside source control.

## 7. Planned Deliverables

1. Project definition, synopsis, and Software Requirements Specification.
2. Reproducible synthetic-data generator and raw CSV files.
3. Data dictionary and data-quality cleaning log.
4. Python cleaning and analysis scripts with generated clean CSV files.
5. Oracle star-schema SQL, ER diagram, loader, queries, and PL/SQL component.
6. At least five analysis charts and a documented Jupyter notebook.
7. Streamlit dashboard with KPI tiles, filters, and interactive charts.
8. Power BI data-model instructions, DAX measures, and three-page report.
9. Excel analysis workbook with Power Query steps, pivots, and dashboard.
10. Automated test results, README, final report, and viva preparation material.

## 8. Ten-Day Implementation Schedule

| Day | Work | Prompts | Deliverable |
|---|---|---|---|
| 1 | Project definition, synopsis, and SRS | P1–P3 | Definition, synopsis, and SRS |
| 2 | Dataset design/generation and data dictionary | P4–P5 | Generator, raw CSVs, and data dictionary |
| 3 | Data cleaning and quality log | P6 | Cleaning script, clean CSVs, and quality log |
| 4 | Star schema and ER diagram | P7 | Oracle schema and diagram |
| 5 | Oracle SQL/PLSQL loader and seven business queries | P8 | Loader and query results |
| 6 | Python analysis, charts, and notebook | P9–P10 | Charts and analysis notebook |
| 7 | Streamlit dashboard | P11 | Interactive dashboard |
| 8 | Power BI data model and three-page report | P12–P13 | PBIX file and report documentation |
| 9 | Excel workbook and automated tests | P14–P15 | Excel workbook and test results |
| 10 | README, final report, viva preparation, debugging, and final review | P16–P20 | Submission-ready repository and review checklist |

## 9. Expected Outcome

The expected outcome is a complete and reproducible inventory-analysis workflow that converts raw inventory-related records into validated datasets, database outputs, visual analysis, and dashboards. The project should make it possible to investigate stock availability, stock-out patterns, reorder risks, inventory value, and supplier delivery performance.

All reported metrics and conclusions will be calculated from the actual generated or selected data. Any limitations caused by synthetic data, assumptions, or unavailable Oracle/Power BI desktop tooling will be stated clearly.

## 10. Project Evaluation

The project will be evaluated on:
- Correctness and reproducibility of data generation and cleaning.
- Traceability of data-quality corrections.
- Validity of the Oracle schema, SQL queries, and PL/SQL logic.
- Accuracy and clarity of Python analysis and visualisations.
- Functionality and usability of the Streamlit, Excel, and Power BI outputs.
- Agreement of key totals across Python and SQL.
- Automated test results, documentation quality, and ability to explain the work during viva.
