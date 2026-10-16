# Query layer

Run `src/pipeline.py` first. It loads the engineered CSV into the `customers` table and executes every view in `analysis.sql`. The populated database is `data/processed/customer_intelligence.sqlite`. It can be opened in DB Browser for SQLite, DBeaver or Python's standard sqlite3 library.

| Business question | View / output | What the answer can establish |
|---|---|---|
| 1. Loyal vs discount-only shoppers | q1_segments | Explicit history/cadence x current promo cohorts; cannot establish discount-only purchasing |
| 2. Behaviors predicting durable value | q2_behavior; loyalty_definitions | Descriptive relationships and competing proxy definitions; no future prediction without outcomes |
| 3. Geographic/demographic opportunities | q3_geography; q3_demographics | Screen/rank candidates using spend, promo exposure and sample size; no market penetration or CAC claim |
| 4. Promo restructuring | q4_promo | Eligibility counts and sales exposure; margin scenarios are calculated separately under declared assumptions |
| 5. Ideal customer profile | q5_icp | Explicit seed cohort with category, age, payment and cadence composition |
| Category and seasonal patterns | category_funnel; season_patterns | Low/mid/high history mix, not actual entry-to-repeat transitions |

Example:

```sql
SELECT * FROM q1_segments;
SELECT * FROM q3_geography WHERE screen_qualified=1 ORDER BY opportunity_rank;
SELECT * FROM customers WHERE sunset_eligible=1;
```

Every view is exported to CSV for reviewers without SQL software. Operational segment labels map exactly to loyalty_a and promo_exposed. No label named churn, at-risk or tenure is fabricated.
