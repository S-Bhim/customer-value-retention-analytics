-- SQLite 3 syntax; all claims trace to customer features, no invented churn labels.
DROP VIEW IF EXISTS q1_segments;
CREATE VIEW q1_segments AS
SELECT segment, COUNT(*) customers, SUM(purchase_amount_usd) observed_sales_usd,
 AVG(purchase_amount_usd) aov_usd, AVG(promo_exposed) promo_rate,
 AVG(loyalty_a) loyalty_proxy_rate, AVG(previous_purchases) mean_previous_purchases,
 AVG(satisfied) satisfied_share_all, AVG(review_rating) mean_known_rating
FROM customers GROUP BY segment;
-- Q2: descriptive associations, NOT forecasts of future loyalty or CLV.
DROP VIEW IF EXISTS q2_behavior;
CREATE VIEW q2_behavior AS
SELECT cadence_group, satisfaction_flag, COUNT(*) customers,
 AVG(purchase_amount_usd) aov_usd, AVG(previous_purchases) mean_previous_purchases,
 AVG(high_history) high_history_rate, AVG(promo_exposed) promo_rate
FROM customers GROUP BY cadence_group,satisfaction_flag;
DROP VIEW IF EXISTS q3_geography;
CREATE VIEW q3_geography AS
SELECT state, customers, observed_sales_usd, aov_usd,promo_rate,loyalty_proxy_rate,
 full_price_sales_usd,smoothed_full_price_spend_per_customer,opportunity_rank,screen_qualified
FROM geography ORDER BY screen_qualified DESC,opportunity_rank;
DROP VIEW IF EXISTS q3_demographics;
CREATE VIEW q3_demographics AS
SELECT age_band,gender,COUNT(*) customers,AVG(purchase_amount_usd) aov_usd,
 AVG(promo_exposed) promo_rate,AVG(loyalty_a) loyalty_proxy_rate
FROM customers GROUP BY age_band,gender;
DROP VIEW IF EXISTS q4_promo;
CREATE VIEW q4_promo AS
SELECT segment, satisfaction_flag, COUNT(*) customers,
 SUM(purchase_amount_usd) observed_sales_usd,SUM(sunset_eligible) sunset_eligible,
 AVG(promo_exposed) promo_rate,
 SUM(CASE WHEN promo_exposed=1 THEN purchase_amount_usd ELSE 0 END)*1.0/SUM(purchase_amount_usd) promo_sales_share
FROM customers GROUP BY segment,satisfaction_flag;
DROP VIEW IF EXISTS q5_icp;
CREATE VIEW q5_icp AS
SELECT age_band,gender,category,payment_method,cadence_group,COUNT(*) customers,
 AVG(purchase_amount_usd) aov_usd
FROM customers WHERE value_tier='High' AND loyalty_a=1 AND promo_exposed=0 AND satisfied=1
GROUP BY age_band,gender,category,payment_method,cadence_group;
DROP VIEW IF EXISTS category_funnel;
CREATE VIEW category_funnel AS
SELECT category,history_band,COUNT(*) customers,AVG(purchase_amount_usd) aov_usd,
 AVG(promo_exposed) promo_rate FROM customers GROUP BY category,history_band;
DROP VIEW IF EXISTS season_patterns;
CREATE VIEW season_patterns AS
SELECT season,history_band,COUNT(*) customers,AVG(purchase_amount_usd) aov_usd,
 AVG(promo_exposed) promo_rate FROM customers GROUP BY season,history_band;
DROP VIEW IF EXISTS loyalty_definitions;
CREATE VIEW loyalty_definitions AS
SELECT 'A: history + cadence' definition,loyalty_a selected,COUNT(*) customers,
 AVG(purchase_amount_usd) aov_usd,AVG(annual_spend_proxy_usd) annual_spend_proxy,
 AVG(satisfied) satisfied_rate FROM customers GROUP BY loyalty_a
UNION ALL
SELECT 'B: history + satisfaction',loyalty_b,COUNT(*),AVG(purchase_amount_usd),
 AVG(annual_spend_proxy_usd),AVG(satisfied) FROM customers GROUP BY loyalty_b;
