# StockWise Viva Preparation — 10 Questions

Try answering each question aloud in your own words before reading the sample answer.

## 1. What is StockWise, and why did you choose this problem?

**Sample answer:** StockWise is an inventory and stock-out analysis project. It identifies products that are out of stock or below their reorder level, calculates inventory value, and measures supplier delivery performance. These metrics help an inventory team decide which items need review.

**Topics:** problem definition, business value, objectives.

## 2. Why did you use synthetic data and a fixed random seed?

**Sample answer:** A suitable licensed real dataset was not selected for the initial build, so I generated synthetic teaching data. A fixed seed makes the data reproducible. I can rerun the generator and get the same records, which makes testing and demonstration easier.

**Topics:** Python, NumPy, reproducibility, data source.

## 3. How did you clean the data using Pandas?

**Sample answer:** I used `duplicated()` to detect exact duplicate rows, `drop_duplicates`-style filtering to retain the first copy, `isna()` to find missing values, and string operations such as `strip()` and `upper()` to standardise labels. Every correction is written to a cleaning log.

**Topics:** Python, Pandas, data quality, traceability.

## 4. What is the difference between a fact table and a dimension table?

**Sample answer:** A fact table stores measurable events or quantities, such as inventory snapshots, stock movements, or purchase orders. A dimension table stores descriptive information used to group and filter those facts, such as product, supplier, or date details.

**Topics:** data modelling, star schema, dimensions and facts.

## 5. What are primary keys and foreign keys in your schema?

**Sample answer:** A primary key uniquely identifies a row in a table. A foreign key references a key in another table. For example, FACT_INVENTORY contains product_key, which refers to DIM_PRODUCT.product_key. This helps prevent fact records from referring to products that do not exist in the dimension.

**Topics:** Oracle SQL, relational integrity.

## 6. Explain one SQL query used in the project.

**Sample answer:** The stock-status query joins FACT_INVENTORY with DIM_PRODUCT, groups rows by product category, and uses SUM with CASE expressions to count stock-out and low-stock products. GROUP BY produces one summary row per category.

**Topics:** SQL JOIN, GROUP BY, CASE, SUM, COUNT.

## 7. What is PL/SQL, and what does your stored procedure do?

**Sample answer:** PL/SQL is Oracle's procedural extension to SQL. The project procedure opens a SYS_REFCURSOR containing products whose available quantity is at or below the reorder level. A calling application can fetch those result rows.

**Topics:** Oracle PL/SQL, stored procedures, cursors.

## 8. How do you calculate supplier lead time and a delayed delivery?

**Sample answer:** Lead time is actual delivery date minus order date, measured in calendar days. A delivery is delayed when its actual date is later than the expected delivery date. In the cleaned synthetic dataset, average lead time is 8.47 days and 149 of 240 orders are delayed.

**Topics:** business metrics, Pandas date operations, SQL date calculations.

## 9. What is the difference between a Power BI relationship and a DAX measure?

**Sample answer:** A relationship connects tables through matching keys and controls how filters move between them. A DAX measure is a calculation evaluated in the current filter context, such as Stock-Out Products or Inventory Value. USERELATIONSHIP can use an inactive date relationship for an alternate date role.

**Topics:** Power BI data modelling, cardinality, DAX, filter context.

## 10. What are the main findings and limitations of your project?

**Sample answer:** In the generated snapshot, 33 products are stock-out and 14 are low stock. There are 149 delayed orders out of 240. These results suggest that stock availability and supplier delivery reliability should be reviewed. However, the data is synthetic, inventory has only one snapshot, and the Oracle and Power BI Desktop outputs still need environment-based validation.

**Topics:** business insights, recommendations, honest reporting, limitations.

## Self-evaluation rubric

Score each answer from 0 to 2:

- **0 — Not yet:** answer is missing or incorrect.
- **1 — Developing:** main idea is correct but explanation or example is incomplete.
- **2 — Ready:** clear explanation, correct terminology, and a project-specific example.

| Score | Interpretation |
|---:|---|
| 0–8 | Revisit the project basics and data flow. |
| 9–14 | Good foundation; practise SQL, DAX, and explaining results. |
| 15–18 | Strong understanding; refine technical details. |
| 19–20 | Viva-ready; practise concise answers without reading notes. |

## Final viva tip

When asked about a result, explain four things: **what was measured, how it was calculated, what the result means, and what limitation applies.** Never describe synthetic results as real company findings or claim Oracle/PBIX execution that has not happened.
