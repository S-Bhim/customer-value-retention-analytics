"""Create an embedded-data Power BI Project (PBIP/PBIR + TMSL)."""
import base64,json,zlib
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
B=R/'powerbi'; REPORT=B/'Founder.Report'; MODEL=B/'Founder.SemanticModel'
BASE='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
def write(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2),encoding='utf-8')
MEASURES={
 'Customers':('COUNTROWS(Customers)','#,0'),
 'Observed sales USD':('SUM(Customers[purchase_amount_usd])','$#,0'),
 'Average order USD':('DIVIDE([Observed sales USD], [Customers])','$0.00'),
 'Promo customer share':('AVERAGE(Customers[promo_exposed])','0.0%'),
 'Promo sales share':('DIVIDE(CALCULATE([Observed sales USD], Customers[promo_exposed] = 1), [Observed sales USD])','0.0%'),
 'Repeat cadence proxy':('AVERAGE(Customers[loyalty_a])','0.0%'),
 'High history share':('AVERAGE(Customers[high_history])','0.0%'),
 'Annual spend proxy USD':('SUM(Customers[annual_spend_proxy_usd])','$#,0'),
 'Observed sales share':('DIVIDE([Observed sales USD], CALCULATE([Observed sales USD], REMOVEFILTERS(Customers[value_tier])))','0.0%'),
 'Full price sales USD':('CALCULATE([Observed sales USD], Customers[promo_exposed] = 0)','$#,0'),
 'Full price spend per customer':('DIVIDE([Full price sales USD], [Customers])','$0.00'),
 'Smoothed full price spend':('DIVIDE([Full price sales USD] + 50 * CALCULATE([Full price spend per customer], REMOVEFILTERS(Customers[state_country])), [Customers] + 50)','$0.00'),
 'Sunset eligible customers':('SUM(Customers[sunset_eligible])','#,0')}
def expr(v):return {'expr':{'Literal':{'Value':v}}}
def field(name,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':'Customers'}},'Property':name}}
def projection(name,measure=False):return {'field':field(name,measure),'queryRef':'Customers.'+name,'nativeQueryRef':name}
def visual(name,typ,x,y,w,h,roles,title,subtitle=''):
    v={'$schema':BASE+'visualContainer/2.4.0/schema.json','name':name,'position':{'x':x,'y':y,'z':0,'height':h,'width':w,'tabOrder':0},'visual':{'visualType':typ,'query':{'queryState':{role:{'projections':[projection(n,m) for n,m in ns]} for role,ns in roles.items()}},'visualContainerObjects':{'title':[{'properties':{'show':expr('true'),'text':expr("'"+title.replace("'","''")+"'"),'fontSize':expr('13D')}}]},'drillFilterOtherVisuals':True}}
    if subtitle:v['visual']['visualContainerObjects']['subTitle']=[{'properties':{'show':expr('true'),'text':expr("'"+subtitle.replace("'","''")+"'")}}]
    write(REPORT/'definition/pages/Founder/visuals'/name/'visual.json',v)
def main():
    d=pd.read_csv(R/'data/processed/customers_features.csv')
    d['state_country']=d.state+', United States'
    cols=[];transforms=[]
    for c in d:
        typ='int64' if pd.api.types.is_integer_dtype(d[c]) else 'double' if pd.api.types.is_numeric_dtype(d[c]) else 'string'
        col={'name':c,'dataType':typ,'sourceColumn':c,'summarizeBy':'none'}
        if c=='state_country':col['dataCategory']='Place'
        if c=='value_tier':col['sortByColumn']='value_tier_order'
        cols.append(col);transforms.append('{"'+c+'", '+{'int64':'Int64.Type','double':'type number','string':'type text'}[typ]+'}')
    rows=[[None if pd.isna(v) else str(v) for v in row] for row in d.itertuples(index=False,name=None)]
    compressor=zlib.compressobj(wbits=-15);payload=json.dumps(rows,separators=(',',':')).encode()
    encoded=base64.b64encode(compressor.compress(payload)+compressor.flush()).decode()
    names=', '.join('"'+c+'"' for c in d.columns)
    m='let\n Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("'+encoded+'", BinaryEncoding.Base64), Compression.Deflate)), {'+names+'}),\n Typed = Table.TransformColumnTypes(Source, {'+', '.join(transforms)+'}, "en-US")\nin Typed'
    model={'name':'Founder','compatibilityLevel':1567,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','tables':[{'name':'Customers','columns':cols,'partitions':[{'name':'Customers','mode':'import','source':{'type':'m','expression':m.splitlines()}}],'measures':[{'name':name,'expression':e,'formatString':fmt} for name,(e,fmt) in MEASURES.items()]}],'annotations':[{'name':'PBI_QueryOrder','value':'["Customers"]'}]}}
    write(MODEL/'model.bim',model)
    write(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'1.0','settings':{}})
    write(B/'Founder.pbip',{'version':'1.0','artifacts':[{'report':{'path':'Founder.Report'}}],'settings':{'enableAutoRecovery':True}})
    write(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../Founder.SemanticModel'}}})
    write(REPORT/'definition/version.json',{'$schema':BASE+'versionMetadata/1.0.0/schema.json','version':'2.0.0'})
    write(REPORT/'definition/report.json',{'$schema':BASE+'report/3.0.0/schema.json','themeCollection':{}})
    write(REPORT/'definition/pages/pages.json',{'$schema':BASE+'pagesMetadata/1.0.0/schema.json','pageOrder':['Founder'],'activePageName':'Founder'})
    write(REPORT/'definition/pages/Founder/page.json',{'$schema':BASE+'page/2.0.0/schema.json','name':'Founder','displayName':'Customer intelligence | proxies','displayOption':'FitToPage','width':1440,'height':960})
    for i,(name,title) in enumerate([('Customers','Customers'),('Observed sales USD','Recorded sales | no time period'),('Promo sales share','Sales with promotion flag'),('Repeat cadence proxy','Repeat cadence proxy | not retention')]):
        visual('KPI'+str(i),'card',20+355*i,10,340,115,{'Values':[(name,True)]},title)
    visual('Pyramid','barChart',20,145,690,360,{'Category':[('value_tier',False)],'Y':[('Customers',True)],'Tooltips':[('Observed sales USD',True),('Observed sales share',True),('Annual spend proxy USD',True)]},'01 | Customer value pyramid','Tiers use annual spend proxy; tooltips show recorded sales')
    visual('PromoRetention','scatterChart',730,145,690,360,{'Category':[('value_tier',False)],'X':[('Promo customer share',True)],'Y':[('Repeat cadence proxy',True)],'Size':[('Observed sales USD',True)]},'02 | Promotion vs repeat cadence, by value tier','Association only; cadence helps define both value and loyalty')
    visual('Geography','filledMap',20,525,690,405,{'Category':[('state_country',False)],'ColorSaturation':[('Smoothed full price spend',True)],'Tooltips':[('Customers',True),('Average order USD',True),('Promo customer share',True),('Full price spend per customer',True)]},'03 | Full-price demand opportunity','State-level screening; smoothed full-price spend per customer')
    visual('CategoryHistory','hundredPercentStackedBarChart',730,525,690,405,{'Category':[('category',False)],'Series':[('history_band',False)],'Y':[('Customers',True)],'Tooltips':[('Average order USD',True),('Promo customer share',True)]},'04 | Category history mix','Low / mid / high purchase history; not a conversion funnel')
    (B/'measures.dax').write_text('\n\n'.join(n+' = '+e for n,(e,_) in MEASURES.items()),encoding='utf-8')
    (B/'embedded_source.m').write_text(m,encoding='utf-8')
    write(B/'theme.json',{'name':'Founder Navy Teal','dataColors':['#166e75','#d2a348','#6984ad','#b8c5d7'],'background':'#f4f7fb','foreground':'#10243b','tableAccent':'#166e75'})
    # Verify that the embedded model contains the exact CSV row values.
    recovered=json.loads(zlib.decompress(base64.b64decode(encoded),wbits=-15))
    assert recovered==rows and len(recovered)==3900
    all_files=list(B.rglob('*.json'))+list(B.rglob('*.pbip'))+list(B.rglob('*.pbir'))+list(B.rglob('*.pbism'))+list(B.rglob('*.bim'))
    for p in all_files:json.loads(p.read_text(encoding='utf-8'))
    print('Power BI source generated; embedded rows verified:',len(rows))
if __name__=='__main__':main()
