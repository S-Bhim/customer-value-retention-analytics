"""Reproduce customer intelligence outputs. Run from any working directory."""
from pathlib import Path
import json, sqlite3, hashlib
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'processed'
FREQUENCY = {'Weekly':52, 'Bi-Weekly':26, 'Fortnightly':26, 'Monthly':12, 'Quarterly':4, 'Every 3 Months':4, 'Annually':1}
RENAME = {'Customer ID':'customer_id','Age':'age','Gender':'gender','Item Purchased':'item_purchased','Category':'category','Purchase Amount (USD)':'purchase_amount_usd','Location':'state','Size':'size','Color':'color','Season':'season','Review Rating':'review_rating','Subscription Status':'subscription_status','Shipping Type':'shipping_type','Discount Applied':'discount_applied','Promo Code Used':'promo_code_used','Previous Purchases':'previous_purchases','Payment Method':'payment_method','Frequency of Purchases':'frequency_of_purchases'}

def bootstrap_diff(a,b,seed=42):
    rng=np.random.default_rng(seed)
    draws=np.array([rng.choice(a,len(a),replace=True).mean()-rng.choice(b,len(b),replace=True).mean() for _ in range(3000)])
    return [float(a.mean()-b.mean()),*np.quantile(draws,[.025,.975]).tolist()]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    raw=ROOT/'data/raw/Dataset.csv'
    d=pd.read_csv(raw).rename(columns=RENAME)
    n_raw=len(d); exact_duplicates=int(d.duplicated().sum()); d=d.drop_duplicates().copy()
    for c in d.select_dtypes('object'):
        d[c]=d[c].str.strip()
    assert d.customer_id.is_unique, 'Conflicting duplicate customer IDs require review'
    assert d.customer_id.notna().all()
    for c in ['discount_applied','promo_code_used','subscription_status']:
        assert set(d[c]) <= {'Yes','No'}
    assert d.frequency_of_purchases.isin(FREQUENCY).all()
    assert d.age.between(18,100).all() and d.purchase_amount_usd.gt(0).all()
    assert d.previous_purchases.ge(0).all() and d.review_rating.dropna().between(1,5).all()
    d['annual_orders_proxy']=d.frequency_of_purchases.map(FREQUENCY)
    d['cadence_group']=d.annual_orders_proxy.map({52:'Weekly',26:'Every two weeks',12:'Monthly',4:'Quarterly',1:'Annual'})
    d['promo_exposed']=(d.discount_applied=='Yes').astype(int)
    d['subscriber']=(d.subscription_status=='Yes').astype(int)
    # A single transaction identifies current exposure, not longitudinal dependency.
    d['dependency_score']=100*d.promo_exposed
    d['dependency_band']=np.where(d.promo_exposed.eq(1),'Promo exposed','Full price observed')
    d['satisfaction_flag']=np.select([d.review_rating.isna(),d.review_rating.ge(4),d.review_rating.lt(3.5)],['Unknown','Satisfied','Service recovery'],default='Neutral')
    d['satisfied']=(d.review_rating.ge(4)).astype(int)
    d['annual_spend_proxy_usd']=d.purchase_amount_usd*d.annual_orders_proxy
    d['historical_value_proxy_usd']=d.purchase_amount_usd*(1+d.previous_purchases)
    cuts=d.annual_spend_proxy_usd.quantile([.5,.8]).tolist()
    d['value_tier']=np.select([d.annual_spend_proxy_usd.ge(cuts[1]),d.annual_spend_proxy_usd.ge(cuts[0])],['High','Core'],default='Developing')
    d['value_tier_order']=d.value_tier.map({'High':1,'Core':2,'Developing':3})
    d['high_history']=(d.previous_purchases.ge(26)).astype(int)
    d['loyalty_a']=((d.previous_purchases.ge(26)) & (d.annual_orders_proxy.ge(12))).astype(int)
    d['loyalty_b']=((d.previous_purchases.ge(26)) & (d.review_rating.ge(4))).astype(int)
    d['history_band']=np.select([d.previous_purchases.le(10),d.previous_purchases.ge(26)],['Low history (0-10)','High history (26+)'],default='Mid history (11-25)')
    d['age_band']=pd.cut(d.age,[17,24,34,44,54,64,100],labels=['18-24','25-34','35-44','45-54','55-64','65+']).astype(str)
    d['segment']=np.select([d.loyalty_a.eq(1)&d.promo_exposed.eq(0),d.loyalty_a.eq(1)&d.promo_exposed.eq(1),d.loyalty_a.eq(0)&d.promo_exposed.eq(0)],['Established full price','Established promo exposed','Developing full price'],default='Developing promo exposed')
    d['sunset_eligible']=((d.segment=='Established promo exposed') & (d.value_tier=='High') & d.satisfied.eq(1)).astype(int)
    d.to_csv(OUT/'customers_features.csv',index=False)
    summaries={}
    for name,cols in {'segments':['segment'],'value_tiers':['value_tier','value_tier_order'],'geography':['state'],'categories':['category'],'category_history':['category','history_band'],'season_history':['season','history_band'],'demographics':['age_band','gender'],'payments':['payment_method'],'cadence':['cadence_group']}.items():
        g=d.groupby(cols,observed=True,dropna=False).agg(customers=('customer_id','size'),observed_sales_usd=('purchase_amount_usd','sum'),aov_usd=('purchase_amount_usd','mean'),annual_spend_proxy_usd=('annual_spend_proxy_usd','sum'),promo_rate=('promo_exposed','mean'),loyalty_proxy_rate=('loyalty_a','mean'),high_history_rate=('high_history','mean'),satisfied_rate=('satisfied','mean'),mean_previous_purchases=('previous_purchases','mean')).reset_index()
        g['sales_share']=g.observed_sales_usd/d.purchase_amount_usd.sum()
        if name=='geography':
            # Regularize small samples towards national full-price spend per customer.
            fp=d.assign(fp_sales=d.purchase_amount_usd*(1-d.promo_exposed)).groupby('state').fp_sales.sum()
            g['full_price_sales_usd']=g.state.map(fp)
            national=float((d.purchase_amount_usd*(1-d.promo_exposed)).mean())
            g['smoothed_full_price_spend_per_customer']=(g.full_price_sales_usd+50*national)/(g.customers+50)
            g['opportunity_rank']=g.smoothed_full_price_spend_per_customer.rank(method='min',ascending=False).astype(int)
            g['screen_qualified']=((g.customers.ge(60)) & (g.aov_usd.gt(d.purchase_amount_usd.mean())) & (g.promo_rate.lt(d.promo_exposed.mean()))).astype(int)
        g.to_csv(OUT/(name+'.csv'),index=False);summaries[name]=g
    comparison=[]
    for name in ['loyalty_a','loyalty_b']:
        selected=d[d[name].eq(1)];other=d[d[name].eq(0)]
        diff=bootstrap_diff(selected.purchase_amount_usd.to_numpy(),other.purchase_amount_usd.to_numpy())
        comparison.append({'definition':name,'customers':len(selected),'share':len(selected)/len(d),'aov':selected.purchase_amount_usd.mean(),'other_aov':other.purchase_amount_usd.mean(),'aov_lift':selected.purchase_amount_usd.mean()/other.purchase_amount_usd.mean()-1,'aov_difference':diff[0],'aov_ci_low':diff[1],'aov_ci_high':diff[2],'annual_spend_proxy_mean':selected.annual_spend_proxy_usd.mean(),'promo_rate':selected.promo_exposed.mean(),'satisfied_rate':selected.satisfied.mean()})
    pd.DataFrame(comparison).to_csv(OUT/'loyalty_comparison.csv',index=False)
    sensitivity=[]
    for history in [20,26,30,38]:
        for cadence in [4,12,26]:
            mask=(d.previous_purchases.ge(history)&d.annual_orders_proxy.ge(cadence))
            sensitivity.append({'history_threshold':history,'annual_order_threshold':cadence,'customers':int(mask.sum()),'share':float(mask.mean()),'aov_usd':float(d.loc[mask,'purchase_amount_usd'].mean())})
    pd.DataFrame(sensitivity).to_csv(OUT/'threshold_sensitivity.csv',index=False)
    # Restrict comparison to male non-subscribers to expose the overlap problem.
    cohort=d[(d.gender=='Male') & d.subscriber.eq(0)]
    overlap=bootstrap_diff(cohort.loc[cohort.promo_exposed.eq(1),'purchase_amount_usd'].to_numpy(),cohort.loc[cohort.promo_exposed.eq(0),'purchase_amount_usd'].to_numpy())
    checks={'raw_rows':n_raw,'clean_rows':len(d),'exact_duplicates_removed':exact_duplicates,'unique_customers':int(d.customer_id.nunique()),'missing_review_ratings':int(d.review_rating.isna().sum()),'missing_review_pct':float(d.review_rating.isna().mean()),'promo_fields_identical':bool(d.discount_applied.eq(d.promo_code_used).all()),'female_promo_customers':int(d.loc[d.gender=='Female','promo_exposed'].sum()),'subscribers_without_promo':int(((d.subscriber==1)&(d.promo_exposed==0)).sum()),'male_nonsubscriber_aov_difference_ci':overlap,'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest()}
    observed=float(d.purchase_amount_usd.sum()); promo=float(d.loc[d.promo_exposed.eq(1),'purchase_amount_usd'].sum()); eligible=d[d.sunset_eligible.eq(1)]
    # Scenario only: purchase amount is assumed to be post-discount revenue here.
    scenarios=[]
    base=float(eligible.purchase_amount_usd.sum())
    for discount in [.10,.15,.20]:
        for cogs in [.4,.6,.75]:
            for loss in [0,.05,.10,.20]:
                list_sales=base/(1-discount); baseline_gp=base-cogs*list_sales
                future_sales=list_sales*(1-loss); future_gp=(1-loss)*list_sales*(1-cogs)
                scenarios.append({'assumed_discount':discount,'cogs_share_of_list':cogs,'volume_loss':loss,'eligible_customers':len(eligible),'observed_cohort_sales':base,'baseline_gross_profit':baseline_gp,'scenario_sales':future_sales,'scenario_gross_profit':future_gp,'gross_profit_change':future_gp-baseline_gp,'revenue_breakeven_loss':discount,'gp_breakeven_loss':discount/(1-cogs)})
    pd.DataFrame(scenarios).to_csv(OUT/'margin_scenarios.csv',index=False)
    icp=d[(d.value_tier=='High')&d.loyalty_a.eq(1)&d.promo_exposed.eq(0)&d.satisfied.eq(1)]
    profile=[]
    for field in ['age_band','gender','category','payment_method','cadence_group','state']:
        for label,n in icp[field].value_counts().items():
            base_share=float(d[field].eq(label).mean());share=n/max(len(icp),1)
            profile.append({'field':field,'level':label,'icp_customers':int(n),'icp_share':share,'base_share':base_share,'index_vs_base':share/base_share})
    pd.DataFrame(profile).to_csv(OUT/'icp_profile.csv',index=False)
    metrics={'customers':len(d),'observed_sales_usd':observed,'aov_usd':observed/len(d),'promo_customers':int(d.promo_exposed.sum()),'promo_customer_rate':float(d.promo_exposed.mean()),'promo_sales_usd':promo,'promo_sales_share':promo/observed,'loyalty_a_count':int(d.loyalty_a.sum()),'loyalty_a_rate':float(d.loyalty_a.mean()),'loyalty_b_count':int(d.loyalty_b.sum()),'definition_jaccard':float(((d.loyalty_a==1)&(d.loyalty_b==1)).sum()/((d.loyalty_a==1)|(d.loyalty_b==1)).sum()),'annual_spend_tier_cuts':cuts,'sunset_eligible_customers':len(eligible),'sunset_observed_sales':base,'icp_customers':len(icp),'loyalty_comparison':comparison,'data_quality':checks}
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    conn=sqlite3.connect(OUT/'customer_intelligence.sqlite')
    d.to_sql('customers',conn,index=False,if_exists='replace')
    for name,g in summaries.items():g.to_sql(name,conn,index=False,if_exists='replace')
    conn.executescript((ROOT/'sql/analysis.sql').read_text(encoding='utf-8'))
    queries=['q1_segments','q2_behavior','q3_geography','q3_demographics','q4_promo','q5_icp','category_funnel','season_patterns','loyalty_definitions']
    for q in queries:pd.read_sql_query('SELECT * FROM '+q,conn).to_csv(OUT/(q+'.csv'),index=False)
    assert pd.read_sql_query('SELECT SUM(customers) n, SUM(observed_sales_usd) s FROM q1_segments',conn).iloc[0]['n']==len(d)
    assert abs(pd.read_sql_query('SELECT SUM(observed_sales_usd) s FROM q1_segments',conn).iloc[0,0]-observed)<1e-8
    assert len(d)==3900 and d.customer_id.is_unique and d.dependency_score.isin([0,100]).all()
    assert d.loyalty_a.eq((d.previous_purchases.ge(26)&d.annual_orders_proxy.ge(12)).astype(int)).all()
    conn.close()
    (OUT/'validation.json').write_text(json.dumps({'status':'PASS','checks':['Unique IDs and valid ranges','3900 rows preserved','Unknown satisfaction retained','SQL counts reconcile','SQL sales reconcile','Loyalty rules reconcile','Dependency proxy range'], 'quality':checks},indent=2))
    print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
