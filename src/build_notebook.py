from pathlib import Path
import json,contextlib,io,platform,importlib.metadata
R=Path(__file__).resolve().parents[1]
def main():
    cells=[];ns={};count=0
    def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(True)})
    def code(text):
        nonlocal count
        count+=1;buffer=io.StringIO()
        with contextlib.redirect_stdout(buffer):exec(compile(text,'notebook','exec'),ns)
        cells.append({'cell_type':'code','metadata':{},'execution_count':count,'source':text.splitlines(True),'outputs':[{'output_type':'stream','name':'stdout','text':buffer.getvalue().splitlines(True)}]})
    md('# Decoding Customer Value\nPrepared by Soumabha Bhim. Executed analysis walkthrough for the supplied data.\n\nThe canonical cleaning/feature logic is `src/pipeline.py`; run it before this notebook if regenerating outputs. No timestamps or churn labels exist, so retention and customer value are explicit proxies. All outputs below come from the included customer files and SQL database.')
    # Generate using a root binding; notebook source independently discovers the extracted project root.
    setup="from pathlib import Path\nimport pandas as pd, json, sqlite3\nROOT = Path.cwd()\nif not (ROOT/'data').exists(): ROOT=ROOT.parent\nP=ROOT/'data/processed'\nd=pd.read_csv(P/'customers_features.csv')\nraw=pd.read_csv(ROOT/'data/raw/Dataset.csv')\nmetrics=json.loads((P/'metrics.json').read_text())\nprint('Customer rows:',len(d),'| Original fields:',len(raw.columns),'| Engineered total:',len(d.columns))"
    import os
    old=Path.cwd();os.chdir(R)
    try:
        code(setup)
        md('## 1. Audit and cleaning\nMissing ratings remain Unknown. Frequency synonyms are normalized. Promo and discount flags must not be added as separate signals.')
        code("print(raw.isna().sum()[raw.isna().sum()>0].to_string())\nprint(pd.crosstab(raw.Gender,raw['Discount Applied']).to_string())\nprint(pd.crosstab(raw['Subscription Status'],raw['Discount Applied']).to_string())\nprint('Promo and discount identical:',raw['Promo Code Used'].eq(raw['Discount Applied']).all())")
        md('## 2. Inspect engineered metrics\nDependency score is current-purchase exposure (0/100), not historical dependence. Annual spend proxy assumes stable basket and stated frequency. High/Core tiers use fixed full-sample thresholds $1,924/$572; satisfaction >=4; missing satisfaction Unknown.')
        code("print(d[['customer_id','annual_orders_proxy','dependency_score','annual_spend_proxy_usd','value_tier','satisfaction_flag','loyalty_a','loyalty_b','segment']].head(12).to_string(index=False))\nprint(pd.read_csv(P/'value_tiers.csv').to_string(index=False))")
        md('## 3. Test competing loyalty definitions\nA = previous purchases >=26 and annual cadence >=12. B = previous purchases >=26 and known rating >=4. A is the primary operational repeat-behavior proxy. B shows a small independent AOV lift, while A does not. A better captures repeat cadence; neither is validated for future retention. Annual-spend differences for A are partly circular. Bootstrap intervals are exploratory, unadjusted and assume independent customers.')
        code("print(pd.read_csv(P/'loyalty_comparison.csv').round(4).to_string(index=False))\nprint('Jaccard overlap:',round(metrics['definition_jaccard'],4))\nprint(pd.read_csv(P/'threshold_sensitivity.csv').round(3).to_string(index=False))")
        md('## 4. SQL answers to all five questions\nThese outputs are descriptive. No view establishes causal discount dependency, future prediction or market underpenetration.')
        code("conn=sqlite3.connect(P/'customer_intelligence.sqlite')\nfor view in ['q1_segments','q2_behavior','q3_geography','q3_demographics','q4_promo','q5_icp']:\n    print('\\n'+view)\n    print(pd.read_sql_query('SELECT * FROM '+view+' LIMIT 8',conn).round(3).to_string(index=False))")
        md('## 5. Category / season history composition\nHistory counts refer to the brand, not the observed category. These are not observed customer journeys or tenure.')
        code("for view in ['category_funnel','season_patterns']:\n    print('\\n'+view)\n    print(pd.read_sql_query('SELECT * FROM '+view,conn).round(3).to_string(index=False))\nconn.close()")
        md('## 6. Margin sensitivity and pilot\n74 customers meet the exact sunset trigger. Assumptions: recorded amount is net revenue, 15% discount, COGS 60% of list sales; scenarios illustrate full removal. The first live test would reduce the current discount by 5 percentage points after instrumentation. A 37/37 pilot is a feasibility test, not proof of non-inferior sales.')
        code("scenarios=pd.read_csv(P/'margin_scenarios.csv')\nprint(scenarios[(scenarios.assumed_discount==.15)&(scenarios.cogs_share_of_list==.6)].round(2).to_string(index=False))\nprint('Eligible customers:',int(d.sunset_eligible.sum()))")
        md('## 7. Ideal customer profile\n103-customer seed: High tier + loyalty A + satisfied + current full-price observation. Frequency is mechanically selected, and gender composition is biased by offer eligibility. Use behavior and category creative with randomized acquisition testing.')
        code("profile=pd.read_csv(P/'icp_profile.csv')\nprint(profile.groupby('field',sort=False).head(3).round(3).to_string(index=False))\nprint('Checks:',json.loads((P/'validation.json').read_text())['status'])")
        md('## 8. Reproduce / extend\nFrom the project root: `python -m pip install -r requirements.txt`, then `python run_project.py`.\n\nOpen `powerbi/Founder.pbip` for the native authored report. Power BI Desktop refresh and visuals require local verification; schema validation is not a Desktop execution test. Open `dashboard/Founder_Dashboard.html` for the portable interactive companion. The PDFs provide findings, a phased plan and a one-page executive summary. Collect dates, real discounts, costs, assignment and future outcomes before attempting survival analysis, causal treatment effects or genuine retention modeling.')
    finally:os.chdir(old)
    out=R/'notebooks/Customer_Intelligence.ipynb';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({'cells':[dict(cell,id='cell-'+str(i)) for i,cell in enumerate(cells)],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':platform.python_version()}},'nbformat':4,'nbformat_minor':5},indent=2),encoding='utf-8')
    print('Executed notebook:',count,'code cells')
if __name__=='__main__':main()
