# StockWise analysis charts

Run after generating and cleaning the datasets:

```bash
python src/01_generate_data.py
python src/02_clean_data.py
python src/04_analysis_charts.py
```

The script creates seven PNG charts in this directory:
1. Available inventory by category.
2. Stock status counts by category.
3. Monthly IN/OUT movement trend.
4. Average supplier delivery lead time.
5. Top products by reorder gap.
6. Inventory value by category.
7. Estimated average daily stock-out products by month.

The stock-out trend is reconstructed from opening quantities and dated stock
movements. It is an estimate, not a sequence of measured daily inventory
snapshots. Inventory value follows available quantity multiplied by unit cost.
All figures are calculated from the generated synthetic dataset.
