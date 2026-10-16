"""Check delivered source, reconciliation and report schemas without Desktop."""
from pathlib import Path
import json,sqlite3,warnings
import pandas as pd
import jsonschema
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
def main():
 d=pd.read_csv(R/'data/processed/customers_features.csv')
 assert len(d)==3900 and d.customer_id.is_unique
 assert d.review_rating.isna().sum()==37
 assert d.purchase_amount_usd.sum()==233081
 assert d.loyalty_a.sum()==1086 and d.loyalty_b.sum()==817
 assert d.sunset_eligible.sum()==74
 conn=sqlite3.connect(R/'data/processed/customer_intelligence.sqlite')
 assert conn.execute('SELECT SUM(customers),SUM(observed_sales_usd) FROM q1_segments').fetchone()==(3900,233081)
 conn.close()
 assert len(PdfReader(R/'reports/Executive_Summary.pdf').pages)==1
 model=json.loads((R/'powerbi/Founder.SemanticModel/model.bim').read_text())
 columns={c['name'] for c in model['model']['tables'][0]['columns']}
 measures={m['name'] for m in model['model']['tables'][0]['measures']}
 schemas={}
 index=json.loads((R/'validation/schemas/index.json').read_text())
 for url,filename in index.items():
  schemas[url]=json.loads((R/'validation/schemas'/filename).read_text())
 validated=0
 warnings.filterwarnings('ignore',category=DeprecationWarning)
 for p in (R/'powerbi/Founder.Report/definition').rglob('*.json'):
  doc=json.loads(p.read_text());url=doc['$schema'];schema=schemas[url]
  jsonschema.Draft7Validator(schema,resolver=jsonschema.RefResolver(url,schema,store=schemas)).validate(doc)
  validated+=1
  if 'visual' in doc:
   for role in doc['visual']['query']['queryState'].values():
    for projection in role['projections']:
     f=projection['field']
     if 'Measure' in f:assert f['Measure']['Property'] in measures
     if 'Column' in f:assert f['Column']['Property'] in columns
 assert validated==12
 result={'status':'PASS','report_schema_files':validated,'unique_customers':3900,'observed_sales_usd':233081,'one_page_summary':True,'visual_model_bindings':'PASS','desktop_runtime_tested':False}
 (R/'validation/final_checks.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
