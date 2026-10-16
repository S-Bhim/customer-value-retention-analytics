# Feature dictionary and decision rationale

Raw grain: 1 row/customer, with 1 observed purchase. Original column names are normalized to snake_case. The supplied raw CSV is unchanged.

| Raw field (normalized) | Meaning / treatment |
|---|---|
| customer_id | Unique customer identifier; never used as a predictive feature |
| age | Age in years; validate 18-100 |
| gender | Supplied label; descriptive only because promo overlap is confounded |
| item_purchased | Item in recorded purchase; not full basket/history |
| category | Recorded purchase category; not first or repeat category |
| purchase_amount_usd | Recorded purchase amount; net/gross interpretation not specified |
| state | Location label; all 50 US states, no city data |
| size, color | Recorded item attributes; retained |
| season | Recorded categorical label; no chronological ordering |
| review_rating | Known rating 1-5; 37 missing remain missing |
| subscription_status | Yes/No; does not establish duration or retention |
| shipping_type | Recorded shipping option; no actual cost provided |
| discount_applied | Yes/No current purchase flag |
| promo_code_used | Yes/No; identical to discount_applied, retained for audit |
| previous_purchases | Accumulated brand order count; no dates or tenure duration |
| payment_method | Recorded payment option; descriptive preference only |
| frequency_of_purchases | Stated cadence; self-report/source semantics not independently verified |

| Engineered field | Exact definition | Business decision / limitation |
|---|---|---|
| annual_orders_proxy | Weekly 52; Bi-Weekly/Fortnightly 26; Monthly 12; Quarterly/Every 3 Months 4; Annually 1 | Contact cadence and spend proxy; not observed annual orders |
| cadence_group | Normalized 5-label cadence | Avoid duplicate categories in charts |
| promo_exposed | discount_applied = Yes (1/0) | Current offer-exposure screen |
| subscriber | subscription_status = Yes (1/0) | Audit subscription/offer overlap |
| dependency_score | 100 × promo_exposed, 0 or 100 | Required dependency field; explicitly exposure only; historical reliance unidentifiable |
| dependency_band | Promo exposed / Full price observed | Honest operational display of score |
| satisfaction_flag | Missing=Unknown; >=4=Satisfied; <3.5=Service recovery; remaining=Neutral | Initial sunset safeguards and service prioritization |
| satisfied | Known review_rating>=4, else 0 | Satisfied share of all customers; unknown remains separately flagged |
| annual_spend_proxy_usd | purchase_amount_usd × annual_orders_proxy | Potential run-rate under stable basket/cadence; not CLV or forecast |
| historical_value_proxy_usd | purchase_amount_usd × (previous_purchases+1) | Rough scale under stable basket; not realized lifetime revenue |
| value_tier | High >=1924; Core >=572 and <1924; Developing <572 | Fixed 80th/50th full-sample proxy-spend quantiles; ties included |
| value_tier_order | High 1 / Core 2 / Developing 3 | Consistent Power BI sorting |
| high_history | previous_purchases>=26 | Brand history proxy; no tenure interpretation |
| loyalty_a | previous_purchases>=26 AND annual_orders_proxy>=12 | Primary operational repeat-cadence proxy; no retention outcome |
| loyalty_b | previous_purchases>=26 AND known rating>=4 | Alternative experience/satisfaction proxy; missing ratings do not qualify |
| history_band | <=10 low, 11-25 mid, >=26 high | Category mix; no first-time customers observed (minimum=1) |
| age_band | 18-24 / 25-34 / 35-44 / 45-54 / 55-64 / 65+ | Broad descriptive monitoring, not validated acquisition effect |
| segment | loyalty_a × promo_exposed: Established full price (1,0), Established promo exposed (1,1), Developing full price (0,0), Developing promo exposed (0,1) | Traceable treatment groups; Developing is not a churn label |
| sunset_eligible | Established promo exposed AND High tier AND satisfied=1 | 74-person initial feasibility pilot |
| state_country (Power BI only) | state + ', United States' | Disambiguate map geocoding |

## Aggregated measures

Observed sales = sum purchase_amount_usd. Promo customer share = mean promo_exposed. Promo sales share = promo-flagged sales / all recorded sales. Repeat cadence proxy = mean loyalty_a; never label as observed retention. High-history rate = mean high_history. AOV = recorded sales / customer count because each row contains one observed purchase.

State full-price spend/customer = sum(amount × (1-promo_exposed))/state n. Smoothed score = (state full-price sales + 50×national full-price spend/customer)/(state n+50). Screen-qualified = n>=60, state AOV>national AOV and state promo share<national promo share. Opportunity rank sorts smoothed score descending; rank does not prove underpenetration. The 50-customer prior is a declared heuristic.

ICP seed = High tier AND loyalty_a=1 AND promo_exposed=0 AND satisfied=1; 103 customers. Profile index = cohort share / full-base share. No causal interpretation or demographic exclusions are supported.

## Missing data / interpretive guardrails

Missing reviews are not imputed. Unknown satisfaction does not enter the initial pilot or ICP. Satisfied-rate denominators use all customers; average review excludes missing. No recency, genuine tenure, churn score, discount-only label, two-year prediction or actual margin is constructed. Cadence participates in both tier and loyalty A; their association is partly circular.
