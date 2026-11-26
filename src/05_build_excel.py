"""Build the StockWise Excel analysis workbook from cleaned CSV files.

Run from the repository root:
    python src/05_build_excel.py

The workbook is written to excel/StockWise_Analysis.xlsx.
"""
from pathlib import Path
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = BASE_DIR / "data" / "clean"
OUTPUT_DIR = BASE_DIR / "excel"
OUTPUT_FILE = OUTPUT_DIR / "StockWise_Analysis.xlsx"


def read_inputs():
    names = ["products", "suppliers", "inventory", "purchase_orders", "stock_movements"]
    missing = [name for name in names if not (CLEAN_DIR / f"{name}.csv").exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing cleaned datasets: {', '.join(missing)}. Run src/02_clean_data.py first."
        )
    frames = {name: pd.read_csv(CLEAN_DIR / f"{name}.csv") for name in names}
    for col in ("order_date", "expected_delivery_date", "actual_delivery_date"):
        frames["purchase_orders"][col] = pd.to_datetime(frames["purchase_orders"][col])
    frames["stock_movements"]["movement_date"] = pd.to_datetime(frames["stock_movements"]["movement_date"])
    frames["inventory"]["snapshot_date"] = pd.to_datetime(frames["inventory"]["snapshot_date"])
    return frames


def write_frame(ws, frame, table_name):
    ws.append(list(frame.columns))
    for row in frame.itertuples(index=False, name=None):
        values = []
        for value in row:
            if pd.isna(value):
                values.append(None)
            elif hasattr(value, "to_pydatetime"):
                values.append(value.to_pydatetime())
            elif hasattr(value, "item"):
                values.append(value.item())
            else:
                values.append(value)
        ws.append(values)
    end_col = get_column_letter(len(frame.columns))
    end_row = len(frame) + 1
    table = Table(displayName=table_name, ref=f"A1:{end_col}{end_row}")
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showFirstColumn=False,
        showLastColumn=False, showRowStripes=True, showColumnStripes=False
    )
    ws.add_table(table)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{end_col}{end_row}"
    for col_idx, col in enumerate(frame.columns, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max(len(str(col)) + 3, 14), 30)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="244062")
        cell.alignment = Alignment(wrap_text=True)


def main():
    frames = read_inputs()
    products, suppliers = frames["products"], frames["suppliers"]
    inventory, orders, movements = frames["inventory"], frames["purchase_orders"], frames["stock_movements"]

    stock = inventory.merge(products, on="product_id", how="left", validate="one_to_one")
    stock = stock.merge(
        suppliers[["supplier_id", "supplier_name", "region"]],
        on="supplier_id", how="left", validate="many_to_one"
    )
    stock["inventory_value"] = stock["available_quantity"] * stock["unit_cost"]
    stock["stock_status"] = "Healthy"
    stock.loc[
        (stock["available_quantity"] > 0) &
        (stock["available_quantity"] <= stock["reorder_level"]), "stock_status"
    ] = "Low stock"
    stock.loc[stock["available_quantity"] <= 0, "stock_status"] = "Stock-out"
    stock["reorder_gap"] = stock["reorder_level"] - stock["available_quantity"]
    stock_export = stock[[
        "product_id", "product_name", "category", "supplier_id", "supplier_name",
        "available_quantity", "reorder_level", "unit_cost", "inventory_value",
        "stock_status", "reorder_gap", "inventory_id", "snapshot_date",
        "opening_quantity", "received_quantity", "issued_quantity", "reserved_quantity",
        "sku", "region"
    ]].copy()

    orders = orders.merge(
        suppliers[["supplier_id", "supplier_name"]],
        on="supplier_id", how="left", validate="many_to_one"
    )
    orders["lead_time_days"] = (orders["actual_delivery_date"] - orders["order_date"]).dt.days
    orders["is_delayed"] = orders["actual_delivery_date"] > orders["expected_delivery_date"]

    category_summary = stock.groupby("category", as_index=False).agg(
        product_count=("product_id", "nunique"),
        available_units=("available_quantity", "sum"),
        stockout_products=("stock_status", lambda x: int((x == "Stock-out").sum())),
        low_stock_products=("stock_status", lambda x: int((x == "Low stock").sum())),
        inventory_value=("inventory_value", "sum"),
    ).sort_values("category")
    supplier_summary = orders.groupby(
        ["supplier_id", "supplier_name"], as_index=False
    ).agg(
        order_count=("order_id", "count"),
        average_lead_time_days=("lead_time_days", "mean"),
        delayed_orders=("is_delayed", "sum"),
        units_ordered=("quantity_ordered", "sum"),
    ).sort_values("supplier_name")

    totals = {
        "products": int(stock["product_id"].nunique()),
        "available_units": int(stock["available_quantity"].sum()),
        "stockout_products": int((stock["stock_status"] == "Stock-out").sum()),
        "low_stock_products": int((stock["stock_status"] == "Low stock").sum()),
        "inventory_value": round(float(stock["inventory_value"].sum()), 2),
        "purchase_order_lines": len(orders),
        "delayed_orders": int(orders["is_delayed"].sum()),
        "received_units": int(movements.loc[movements["movement_type"] == "IN", "quantity"].sum()),
        "issued_units": int(movements.loc[movements["movement_type"] == "OUT", "quantity"].sum()),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    dash = wb.active
    dash.title = "Dashboard"
    dash.merge_cells("A1:H1")
    dash["A1"] = "StockWise — Inventory & Stock-Out Analysis"
    dash["A1"].font = Font(bold=True, size=18, color="FFFFFF")
    dash["A1"].fill = PatternFill("solid", fgColor="1F3A5F")
    dash["A1"].alignment = Alignment(horizontal="center")
    dash.merge_cells("A2:H2")
    dash["A2"] = "Synthetic teaching dataset | Values recalculate when opened in Excel"
    dash["A2"].font = Font(italic=True, color="64748B")

    kpis = [
        ("A4", "Products", "A5", "=COUNTA(Stock_Analysis!A:A)-1"),
        ("C4", "Available Units", "C5", "=SUM(Stock_Analysis!F:F)"),
        ("E4", "Stock-Out Products", "E5", '=COUNTIF(Stock_Analysis!J:J,"Stock-out")'),
        ("G4", "Inventory Value", "G5", "=SUM(Stock_Analysis!I:I)"),
        ("A7", "Low-Stock Products", "A8", '=COUNTIF(Stock_Analysis!J:J,"Low stock")'),
        ("C7", "Delayed Orders", "C8", "=SUM(Supplier_Summary!D:D)"),
        ("E7", "Received Units", "E8", '=SUMIF(Stock_Movements!D:D,"IN",Stock_Movements!E:E)'),
        ("G7", "Issued Units", "G8", '=SUMIF(Stock_Movements!D:D,"OUT",Stock_Movements!E:E)'),
    ]
    for label_cell, label, value_cell, formula in kpis:
        dash[label_cell] = label
        dash[label_cell].font = Font(bold=True, color="FFFFFF")
        dash[label_cell].fill = PatternFill("solid", fgColor="0F766E")
        dash[label_cell].alignment = Alignment(horizontal="center")
        dash[value_cell] = formula
        dash[value_cell].font = Font(bold=True, size=16, color="1F3A5F")
        dash[value_cell].alignment = Alignment(horizontal="center")
    dash["G5"].number_format = '#,##0.00'
    for col in "ABCDEFGH":
        dash.column_dimensions[col].width = 18

    cat_ws = wb.create_sheet("Category_Summary")
    cat_ws.append(["category", "product_count", "available_units", "stockout_products", "low_stock_products", "inventory_value"])
    for idx, row in enumerate(category_summary.itertuples(index=False), start=2):
        cat_ws.append([
            row.category,
            f'=COUNTIF(Stock_Analysis!C:C,A{idx})',
            f'=SUMIF(Stock_Analysis!C:C,A{idx},Stock_Analysis!F:F)',
            f'=COUNTIFS(Stock_Analysis!C:C,A{idx},Stock_Analysis!J:J,"Stock-out")',
            f'=COUNTIFS(Stock_Analysis!C:C,A{idx},Stock_Analysis!J:J,"Low stock")',
            f'=SUMIF(Stock_Analysis!C:C,A{idx},Stock_Analysis!I:I)',
        ])
    sup_ws = wb.create_sheet("Supplier_Summary")
    sup_ws.append(["supplier_id", "supplier_name", "order_count", "delayed_orders", "average_lead_time_days", "units_ordered"])
    for idx, row in enumerate(supplier_summary.itertuples(index=False), start=2):
        sup_ws.append([
            row.supplier_id, row.supplier_name,
            f'=COUNTIF(Purchase_Orders!B:B,A{idx})',
            f'=COUNTIFS(Purchase_Orders!B:B,A{idx},Purchase_Orders!K:K,TRUE)',
            f'=AVERAGEIF(Purchase_Orders!B:B,A{idx},Purchase_Orders!J:J)',
            f'=SUMIF(Purchase_Orders!B:B,A{idx},Purchase_Orders!G:G)',
        ])

    write_frame(wb.create_sheet("Products"), products, "ProductsTable")
    write_frame(wb.create_sheet("Suppliers"), suppliers, "SuppliersTable")
    write_frame(wb.create_sheet("Inventory"), inventory, "InventoryTable")
    write_frame(wb.create_sheet("Purchase_Orders"), orders, "PurchaseOrdersTable")
    write_frame(wb.create_sheet("Stock_Movements"), movements, "StockMovementsTable")
    write_frame(wb.create_sheet("Stock_Analysis"), stock_export, "StockAnalysisTable")

    check_ws = wb.create_sheet("Cross_Check")
    check_ws.append(["Metric", "Python value", "Oracle SQL value", "Status"])
    for idx, (metric, value) in enumerate(totals.items(), start=2):
        check_ws.append([
            metric.replace("_", " ").title(), value, None,
            f'=IF(C{idx}="","PENDING",IF(ABS(B{idx}-C{idx})<0.01,"PASS","FAIL"))'
        ])
    check_ws["A12"] = "Oracle SQL values remain blank until real Oracle query exports are available."
    check_ws.merge_cells("A12:D12")

    chart1 = BarChart()
    chart1.type = "bar"
    chart1.title = "Available Units by Category"
    chart1.y_axis.title = "Category"
    chart1.x_axis.title = "Available units"
    chart1.add_data(Reference(cat_ws, min_col=3, min_row=1, max_row=cat_ws.max_row), titles_from_data=True)
    chart1.set_categories(Reference(cat_ws, min_col=1, min_row=2, max_row=cat_ws.max_row))
    dash.add_chart(chart1, "A10")

    chart2 = BarChart()
    chart2.type = "bar"
    chart2.title = "Average Supplier Lead Time"
    chart2.y_axis.title = "Supplier"
    chart2.x_axis.title = "Calendar days"
    chart2.add_data(Reference(sup_ws, min_col=5, min_row=1, max_row=sup_ws.max_row), titles_from_data=True)
    chart2.set_categories(Reference(sup_ws, min_col=2, min_row=2, max_row=sup_ws.max_row))
    dash.add_chart(chart2, "E10")

    chart3 = BarChart()
    chart3.type = "col"
    chart3.grouping = "stacked"
    chart3.overlap = 100
    chart3.title = "Stock-Out and Low-Stock Products by Category"
    chart3.y_axis.title = "Products"
    chart3.x_axis.title = "Category"
    chart3.add_data(Reference(cat_ws, min_col=4, max_col=5, min_row=1, max_row=cat_ws.max_row), titles_from_data=True)
    chart3.set_categories(Reference(cat_ws, min_col=1, min_row=2, max_row=cat_ws.max_row))
    dash.add_chart(chart3, "A25")

    instructions = wb.create_sheet("Instructions")
    for row in [
        ["StockWise Excel workbook"],
        ["Source", "Clean synthetic CSV data from data/clean/."],
        ["Refresh", "Regenerate and clean the data, then rerun src/05_build_excel.py."],
        ["Dashboard", "KPI cells and summary tables use Excel formulas; Excel recalculates them on open."],
        ["PivotTables", "Use Insert > PivotTable on the Excel tables to create native PivotTables."],
        ["Slicers", "Select a PivotTable, then PivotTable Analyze > Insert Slicer. Add Category, Supplier, or Stock Status."],
        ["Power Query", "Follow excel/Power_Query_Guide.md to import and clean the CSVs in Excel."],
        ["Cross-check", "Python values are populated. Oracle SQL values are blank and statuses remain PENDING until real Oracle outputs are entered."],
        ["Currency", "The synthetic dataset does not specify a real-world currency; values are dataset currency units."],
    ]:
        instructions.append(row)
    instructions.column_dimensions["A"].width = 22
    instructions.column_dimensions["B"].width = 110
    instructions["A1"].font = Font(bold=True, size=16, color="FFFFFF")
    instructions["A1"].fill = PatternFill("solid", fgColor="244062")
    for row in instructions.iter_rows(min_row=2):
        row[0].font = Font(bold=True)
        row[1].alignment = Alignment(wrap_text=True, vertical="top")

    for sheet in (cat_ws, sup_ws, check_ws):
        sheet.freeze_panes = "A2"
        for col in range(1, sheet.max_column + 1):
            sheet.column_dimensions[get_column_letter(col)].width = 24
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="244062")
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.save(OUTPUT_FILE)

    check = load_workbook(OUTPUT_FILE, read_only=True, data_only=False)
    print(f"Created {OUTPUT_FILE.relative_to(BASE_DIR)} with {len(check.sheetnames)} sheets.")
    print("Python totals:", totals)


if __name__ == "__main__":
    main()
