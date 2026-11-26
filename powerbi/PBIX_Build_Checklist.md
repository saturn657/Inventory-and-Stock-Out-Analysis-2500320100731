# PBIX Build Status and Checklist

## Required output

Expected Power BI Desktop file: `powerbi/StockWise.pbix`.

**Status: Not yet created.** This environment cannot run Power BI Desktop, so no placeholder or renamed text file is being presented as a PBIX.

## Build steps

- [ ] Import the five clean CSV tables.
- [ ] Merge supplier name and region into Products in Power Query.
- [ ] Create and mark DimDate as the date table.
- [ ] Create the seven relationships documented in PowerBI_Data_Model.md and the two inactive purchase-order date relationships.
- [ ] Add core measures from DAX_Measures.md.
- [ ] Add report measures from Report_DAX_Measures.md.
- [ ] Build Inventory Overview page.
- [ ] Build Product & Supplier Analysis page.
- [ ] Build Stock-Out & Reorder Analysis page.
- [ ] Add slicers, sync where required, and configure drill-through.
- [ ] Reconcile KPIs against Python outputs.
- [ ] Save as `powerbi/StockWise.pbix`.
- [ ] Reopen the saved PBIX and verify all pages, visuals, relationships, and slicers.

The PBIX should be marked complete only after the file exists and has been reopened successfully in Power BI Desktop.
