from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];P=R/'data/processed';O=R/'reports/figures';O.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#10243b','text.color':'#10243b'})
v=pd.read_csv(P/'value_tiers.csv').sort_values('value_tier_order');g=pd.read_csv(P/'geography.csv').query('screen_qualified == 1').sort_values('opportunity_rank').head(8)
fig,axs=plt.subplots(2,2,figsize=(13,8.2));fig.patch.set_facecolor('#f4f7fb')
ax=axs[0,0];ax.barh(v.value_tier,v.customers,color=['#166e75','#6984ad','#b8c5d7']);ax.invert_yaxis();ax.set_title('Customer pyramid | annual spend proxy',loc='left',fontweight='bold');ax.set_xlabel('Customers');
for i,(_,r) in enumerate(v.iterrows()):ax.text(r.customers+20,i,f'{r.customers:,} | {r.sales_share:.1%} of observed sales',va='center',fontsize=8)
ax.set_xlim(0,2900)
ax=axs[0,1];ax.scatter(v.promo_rate*100,v.loyalty_proxy_rate*100,s=v.observed_sales_usd/180,color=['#6984ad','#b8c5d7','#166e75'],alpha=.8)
for _,r in v.iterrows():ax.annotate(r.value_tier,(r.promo_rate*100,r.loyalty_proxy_rate*100),xytext=(8,6),textcoords='offset points')
ax.set(xlim=(35,50),ylim=(0,65),xlabel='Customers with promo flag (%)',ylabel='Repeat cadence proxy (%)');ax.set_title('Promo exposure vs repeat cadence proxy',loc='left',fontweight='bold');ax.grid(alpha=.15)
ax=axs[1,0];ax.barh(g.state,g.smoothed_full_price_spend_per_customer,color='#166e75');ax.invert_yaxis();ax.set_title('Geographic test shortlist',loc='left',fontweight='bold');ax.set_xlabel('Smoothed full-price spend per customer (USD)')
c=pd.read_csv(P/'category_history.csv').pivot(index='category',columns='history_band',values='customers');c=c[['Low history (0-10)','Mid history (11-25)','High history (26+)']];c=c.div(c.sum(axis=1),axis=0)*100
c.plot.barh(stacked=True,ax=axs[1,1],color=['#b8c5d7','#6984ad','#166e75']);axs[1,1].set_title('Category history mix | not customer journeys',loc='left',fontweight='bold');axs[1,1].set_ylabel('');axs[1,1].set_xlabel('Share of customers (%)');axs[1,1].legend(['0-10','11-25','26+'],title='Previous purchases',fontsize=8,loc='lower center',bbox_to_anchor=(.5,-.39),ncol=3)
fig.suptitle('DECODING CUSTOMER VALUE',x=.04,ha='left',fontweight='bold',fontsize=19)
fig.text(.04,.015,'Snapshot of 3,900 customers. No dates, churn, costs or discount amounts. Recorded sales are not lifetime revenue.',fontsize=9)
fig.tight_layout(rect=[.025,.06,.98,.95],h_pad=2);fig.savefig(O/'founder_dashboard.png',dpi=160);plt.close(fig)
print('Chart created')
