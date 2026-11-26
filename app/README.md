# StockWise Streamlit dashboard

Run from the repository root:

```bash
python -m pip install -r requirements.txt
python src/01_generate_data.py
python src/02_clean_data.py
streamlit run app/streamlit_app.py
```

The dashboard has four KPI tiles, category/supplier/activity-date filters,
and three interactive Plotly charts. The date filter applies to stock
movements and purchase orders. Inventory KPIs use the latest inventory
snapshot because the generated inventory table contains one snapshot date.

All data is synthetic. The dashboard does not connect to a live inventory
system or place replenishment orders.
