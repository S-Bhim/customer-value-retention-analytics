# Opening and reviewing the Power BI project

## What is included

`Founder.pbip` points to `Founder.Report/definition.pbir` and `Founder.SemanticModel`. The model contains all 3,900 customer rows in a compressed embedded Power Query source, so the initial refresh does not require path editing. `model.bim` includes typed columns and DAX measures. No published workspace, login, credentials or licensed custom visual is required for local source editing.

## Validation status

- JSON parses successfully; 12 report files pass the official Microsoft JSON schemas.
- Embedded rows decompress to the exact engineered CSV data plus a derived US-qualified state field.
- All named visual fields and measures are checked against the semantic model.
- **Power BI Desktop has not been used to open/refresh this project in the execution environment.** Visual role binding, DAX evaluation, M refresh, map geocoding and Desktop-version compatibility need a Desktop check. This is a generated PBIP project, not a tested binary PBIX.
- The accompanying offline HTML dashboard is provided for immediate interactive inspection; it is not a substitute Power BI binary.

## Open

1. Extract the complete ZIP, keeping the report and semantic-model folders beside `Founder.pbip`.
2. Use a current standard Power BI Desktop that supports Power BI Projects and PBIR; the Report Server edition does not support this project workflow.
3. Open `Founder.pbip` (or the report's `definition.pbir`). Refresh when requested to materialize the embedded model.
4. Verify total customers 3,900, recorded sales $233,081, promo sales share 42.65%, repeat cadence proxy 27.85%.
5. Confirm the four panels below. Select a tier/category/state to cross-filter; Ctrl-select for multiple selections. Hover for supporting metrics.
6. Import `theme.json` from View > Themes if you prefer the supplied navy/teal palette.
7. If a `.pbix` submission is required, save a copy from Power BI Desktop after successful refresh and visual inspection.

## Four analytical panels

| Panel | Visual and bindings | Interpretation |
|---|---|---|
| Customer pyramid | Horizontal bar: value_tier, Customers; tooltips sales, sales share, annual spend proxy | Proxy value distribution with observed sales contribution |
| Promo vs retention proxy | Scatter: value_tier details, X Promo customer share, Y Repeat cadence proxy, Size Observed sales USD | Non-causal association; cadence occurs in both tier and repeat rules |
| Geographic opportunity | Filled US state map: state_country, color Smoothed full price spend; tooltips count, AOV, promo share, raw full-price spend/customer | Demand screening, not proven underpenetration |
| Category funnel proxy | 100% stacked horizontal bar: category, history_band, Customers | Cross-sectional low/mid/high history mix, not customer transitions |

The scatter uses value tiers as segments; the four operational segments already encode promo and loyalty and would force meaningless 0/1 scatter coordinates. The required retention measure is visibly labeled a proxy throughout because no temporal retention can be calculated.

## Map and visual fallback

Your Desktop/tenant may disable map visuals or require network access for geocoding. Enable permitted map settings or use a bar/table with state_country, Average order USD, Promo customer share and Smoothed full price spend. A map is already authored in the project; the HTML companion has an offline state tile map without geocoding. If a version-specific role binding is not recognized, use the binding table above to rebind it in Desktop.

## Refresh from a new CSV

For this submission, run `python src/build_powerbi.py` after the main pipeline. It regenerates embedded source and report files, overwriting custom report edits. For ongoing use, replace the table partition with a CSV Power Query source using the same column names/types and maintain the measures. Do not silently change the definition of observed sales or label annual-spend proxies as CLV.

Official format references:

- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
