# Verification record

- Dataset audit: 3,900 unique customer IDs, 18 raw fields, 37 missing review ratings preserved, no duplicates removed.
- Python/SQL: count and $233,081 recorded sales reconciliation; exact loyalty A/B counts 1,086/817; sunset cohort 74; valid engineered rule ranges.
- Notebook: eight Python code cells executed successfully; outputs included.
- Reports: report 10 pages, playbook 3 pages, executive summary 1 page. All pages rendered with Poppler and visually inspected; table headers corrected during review.
- HTML companion: loaded in headless Google Chrome; verified initial totals, 50 states, Footwear subset of 599, combined state/category filters and reset. Preview inspected after scatter-label adjustment. Download action is authored using a local CSV Blob; saving that export was not automated.
- Power BI: model data decompresses exactly to the feature CSV plus derived state_country, all visual column/measure references resolve, 12 PBIR files pass Microsoft's official schemas. Native Power BI Desktop open/refresh, visual rendering, DAX/M execution and map geocoding were not performed.
- Statistical scope: customer bootstrap with 3,000 resamples/group and fixed seed 42; no time-based validation possible. No future/causal/margin outcomes have been invented. Scenario assumptions are explicit.

`validate_project.py` can repeat the deterministic data/SQL/PDF/schema/binding checks after dependency installation. It is not a substitute for a Power BI Desktop check or a prospective customer experiment.
