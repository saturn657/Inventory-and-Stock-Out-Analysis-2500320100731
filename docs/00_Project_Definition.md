# StockWise — Project Definition

## 1. Problem Statement

Retail and distribution businesses must maintain enough inventory to meet demand without tying up excessive money in unsold stock. When product, supplier, stock movement, and replenishment records are scattered or inconsistent, it becomes difficult to identify stock-out risks, low-stock items, inventory value, and supplier delays. StockWise brings these records into a structured analysis workflow using Python, Oracle SQL/PLSQL, Excel, Streamlit, and Power BI. The project turns inventory data into measurable insights that can support better replenishment and stock-control decisions.

## 2. Measurable Objectives

1. **Create reliable datasets:** Generate or obtain structured product, supplier, inventory, and stock-movement data; profile and clean the records; and maintain a log of every identified data-quality issue and its treatment.
2. **Measure inventory position:** Calculate total available units, inventory value, low-stock products, and stock-out products using documented business rules.
3. **Evaluate replenishment performance:** Calculate supplier lead times from order and delivery dates, identify delayed deliveries, and compare supplier performance.
4. **Deliver and validate analysis:** Build Python analysis, Oracle SQL/PLSQL queries, an Excel workbook, a Streamlit dashboard, and a three-page Power BI report; cross-check key totals between the Python and SQL outputs.

## 3. Business Questions

1. Which products and categories experience the highest number of stock-out events?
2. Which products are below their reorder level or are most at risk of running out?
3. Which products and categories contribute the highest inventory value?
4. Which suppliers have the longest replenishment lead times or the most delayed deliveries?
5. How do available inventory levels and stock-out events change over time?

## 4. Business Rules and Metric Definitions

- **Available quantity:** The quantity currently available for sale or use, after accounting for recorded stock movements.
- **Stock-out:** A product is classified as out of stock when its available quantity is less than or equal to zero.
- **Low stock:** A product is classified as low stock when its available quantity is greater than zero and less than or equal to its reorder level.
- **Inventory value:** Available quantity multiplied by unit cost.
- **Supplier lead time:** Delivery date minus purchase-order date, measured in days.
- **Delayed delivery:** A delivery is delayed when its actual delivery date is later than its expected delivery date.
- All metrics will be calculated from the generated or selected dataset; assumptions and limitations will be documented.

## 5. Project Scope

### In scope
- Product, supplier, inventory, purchase-order, and stock-movement data.
- Dataset generation or documented dataset sourcing, data profiling, cleaning, and validation.
- A reproducible Python/Pandas workflow and data-quality log.
- Oracle-compatible relational schema, SQL queries, and PL/SQL components.
- Exploratory analysis, charts, a Jupyter notebook, and a Streamlit dashboard.
- Excel analysis and a Power BI data model and report.
- Automated checks that validate data quality and reconcile important totals.

### Out of scope
- Live integration with a commercial ERP or point-of-sale system.
- Real-time inventory tracking.
- Automatic purchase-order placement.
- Machine-learning forecasting or AI-based recommendations.
- Production deployment for a real business.

## 6. Ten-Day Project Plan

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

## 7. Tools and Technologies

- **Python:** Core programming and analysis.
- **Pandas and NumPy:** Data preparation, transformation, and calculations.
- **Matplotlib:** Static charts and visual analysis.
- **Oracle SQL and PL/SQL:** Relational schema, querying, and database-side logic.
- **Excel:** Power Query, pivot tables, formulas, and dashboard.
- **Power BI:** Data modelling, DAX measures, and interactive reporting.
- **Streamlit:** Interactive Python dashboard.
- **Jupyter Notebook:** Documented exploratory analysis.
- **Git and GitHub:** Version control and project history.

Python dependencies will be listed in `requirements.txt` and installed with pip. Database credentials will be supplied by each user through local configuration/environment variables and will not be committed to the repository.

## 8. Expected Outcome

The completed project will provide a reproducible inventory-analysis workflow, from raw data generation or sourcing through cleaning, database loading, analysis, dashboards, and validation. It is expected to help answer the five business questions with traceable calculations and consistent outputs. If synthetic data is used, it will be clearly labelled as synthetic and results will be presented as illustrative rather than as findings from a real company.
