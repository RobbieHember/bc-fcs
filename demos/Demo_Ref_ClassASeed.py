'''
Climate change mitigation from use of class A seed

Notes:
	- The machine needs to be freshly started to successfully run 8000 stands
	- Running 8000 stands takes 12 min

'''

#%% Import modules
import numpy as np
import matplotlib.pyplot as plt
import warnings
import time
import fcgadgets.macgyver.util_general as gu
import fcgadgets.macgyver.util_inventory as uinv
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun as cbr
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.macgyver.util_demo as udem
import fcgadgets.gaia.gaia_util as gaia
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Configure project
t0=time.time()
meta=u1ha.Init()
pNam='Demo_Ref_ClassASeed'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'D:\Modelling Projects\Demo_Ref_ClassASeed'
meta=cbu.ImportProjectConfig(meta,pNam)
meta['Graphics']['Print Figures']='On'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\Demo\Demo_Ref_ClassASeed'

#%% Prepare inputs
cbu.Write_BatchTIPSY_Input_File(meta,pNam)
cbu.PrepareInventoryFromSpreadsheet(meta,pNam)
cbu.BuildEventChronologyFromSpreadsheet(meta,pNam)
cbu.PrepGrowthCurvesForCBR(meta,pNam)

#%% Run model
meta=cbr.MeepMeep(meta,pNam)

#%% Calculate summaries for future simulations
cbu.Calc_MOS_GHG(meta,pNam)
cbu.Calc_MOS_Econ(meta,pNam)
cbu.Calc_MOS_Area(meta,pNam)
cbu.Calc_MOS_MortByAgent(meta,pNam)

#%% Import data
pNam='Demo_Ref_ClassASeed'
pth=r'D:\Modelling Projects\Demo_Ref_ClassASeed\Inputs\Metadata.pkl'
meta=gu.ipickle(pth)
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
mos=cbu.Import_MOS_ByScnAndStrata_GHGEcon(meta,pNam)
mos[pNam]['Delta']={}
mos[pNam]['Delta']['Interior']={'iB':0,'iP':1}
mos[pNam]['Delta']['Coast']={'iB':2,'iP':3}
mos=cbu.Import_MOS_ByScnComparisonAndStrata(meta,pNam,mos)
mos=cbu.Import_MOS_ByScnAndStrata_Area(meta,pNam,mos)
iPS=0; iSS=0; iYS=0

# Calculate radiative forcing with FAIR
#dRF,mos=gaia.Calc_RF_FAIR(meta,pNam,mos)

t1=time.time()
print('Run time: ' + str((t1-t0)/60) + ' min')

#%% Export tables for each scenario
tbs=udem.Export_Summary_Tables(meta,pNam,mos)

#%% Save to change tracker
udem.Record_In_ChangeTrackerDB(meta,pNam,mos,tbs)

#%% Export tables for each scenario

# Use this to estimate delta at year 100
t0=meta[pNam]['Project']['Year Project']
t1=meta[pNam]['Project']['Year Project']+100
df=udem.ExportSummariesByScenario(meta,pNam,mos,table_name='Summary 2',operTime='Mean',t0=t0,t1=t1)

# Use this to estimate delta growth over next 100 years
t0=meta[pNam]['Project']['Year Project']+1
t1=meta[pNam]['Project']['Year Project']+100
df=udem.ExportSummariesByScenario(meta,pNam,mos,table_name='Summary 3',operTime='Mean',t0=t0,t1=t1)

#%% Area affected over time

tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
plt.close('all'); fig,ax=plt.subplots(1,2,figsize=gu.cm2inch(15,6.5))
# Interior
d=gu.ipickle(meta['Paths'][pNam]['Data'] + '\\Outputs\\Scenario0002\\Data_Scn0002_Ens0001_Bat0001.pkl')
z={}
for k in d['C_M_DistByAgent'].keys():
	idx=d['C_M_DistByAgent'][k]['idx']
	cd=cbu.lut_n2s(meta['LUT']['Event'],k)[0]
	z[cd]=np.zeros( (d['A'].shape),dtype='float')
	z[cd][idx[0],idx[1]]=meta['Core']['Scale Factor C_M_DistByAgent']*d['C_M_DistByAgent'][k]['M'].astype('float')
Af=np.zeros(tv.size)
Ab=np.zeros(tv.size)
Ah=np.zeros(tv.size)
Au=np.zeros(tv.size)
for i in range(tv.size):
	iT=np.where( (tv>=meta[pNam]['Project']['Year Project']+2) & (tv<=tv[i]) )[0]
	fF=np.sum(z['Wildfire'][iT,:],axis=0)
	fB=np.sum(z['Mountain Pine Beetle'][iT,:],axis=0)
	fH=np.sum(z['Harvest'][iT,:],axis=0)
	iS=np.where( (fF<1) & (fB<1) & (fH<1) )[0]; Au[i]=iS.size/meta[pNam]['Project']['N Stand']*100
	iS=np.where( (fF>1) )[0]; Af[i]=iS.size/meta[pNam]['Project']['N Stand']*100
	iS=np.where( (fF<1) & (fB>1) )[0]; Ab[i]=iS.size/meta[pNam]['Project']['N Stand']*100
	iS=np.where( (fF<1) & (fB<1) & (fH>1) )[0]; Ah[i]=iS.size/meta[pNam]['Project']['N Stand']*100
ax[0].bar(tv[iT],Au[iT],1,fc=[0.85,1,0.75],label='Unaffected')
ax[0].bar(tv[iT],Ah[iT],1,bottom=Au[iT],fc=[0.8,0.85,1],label='Harvest')
ax[0].bar(tv[iT],Ab[iT],1,bottom=Au[iT]+Ah[iT],fc=[0.85,0.75,1],label='Beetles')
ax[0].bar(tv[iT],Af[iT],1,bottom=Au[iT]+Ah[iT]+Ab[iT],fc=[1,0.85,0.8],label='Wildfire')
ax[0].legend(loc='lower left',frameon=True,facecolor='w')
ax[0].set(ylabel=r'Area affected (%)',xlabel=r'Time, years',yticks=np.arange(0,110,10),ylim=[0,100],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[0].yaxis.set_ticks_position('both'); ax[0].xaxis.set_ticks_position('both'); ax[0].tick_params(length=meta['Graphics']['gp']['tickl'])
# Coast
d=gu.ipickle(meta['Paths'][pNam]['Data'] + '\\Outputs\\Scenario0004\\Data_Scn0004_Ens0001_Bat0001.pkl')
z={}
for k in d['C_M_DistByAgent'].keys():
	idx=d['C_M_DistByAgent'][k]['idx']
	cd=cbu.lut_n2s(meta['LUT']['Event'],k)[0]
	z[cd]=np.zeros( (d['A'].shape),dtype='float')
	z[cd][idx[0],idx[1]]=meta['Core']['Scale Factor C_M_DistByAgent']*d['C_M_DistByAgent'][k]['M'].astype('float')
Af=np.zeros(tv.size)
Ab=np.zeros(tv.size)
Ah=np.zeros(tv.size)
Au=np.zeros(tv.size)
for i in range(tv.size):
	iT=np.where( (tv>=meta[pNam]['Project']['Year Project']+2) & (tv<=tv[i]) )[0]
	fF=np.sum(z['Wildfire'][iT,:],axis=0)
	fB=np.sum(z['Mountain Pine Beetle'][iT,:],axis=0)
	fH=np.sum(z['Harvest'][iT,:],axis=0)
	iS=np.where( (fF<1) & (fB<1) & (fH<1) )[0]; Au[i]=iS.size/meta[pNam]['Project']['N Stand']*100
	iS=np.where( (fF>1) )[0]; Af[i]=iS.size/meta[pNam]['Project']['N Stand']*100
	iS=np.where( (fF<1) & (fB>1) )[0]; Ab[i]=iS.size/meta[pNam]['Project']['N Stand']*100
	iS=np.where( (fF<1) & (fB<1) & (fH>1) )[0]; Ah[i]=iS.size/meta[pNam]['Project']['N Stand']*100
ax[1].bar(tv[iT],Au[iT],1,fc=[0.85,1,0.75],label='Unaffected')
ax[1].bar(tv[iT],Ah[iT],1,bottom=Au[iT],fc=[0.8,0.85,1],label='Harvest')
ax[1].bar(tv[iT],Ab[iT],1,bottom=Au[iT]+Ah[iT],fc=[0.85,0.75,1],label='Beetles')
ax[1].bar(tv[iT],Af[iT],1,bottom=Au[iT]+Ah[iT]+Ab[iT],fc=[1,0.85,0.8],label='Wildfire')
ax[1].set(ylabel=r'Area affected (%)',xlabel=r'Time, years',yticks=np.arange(0,110,10),ylim=[0,100],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[1].yaxis.set_ticks_position('both'); ax[1].xaxis.set_ticks_position('both'); ax[1].tick_params(length=meta['Graphics']['gp']['tickl'])
plt.tight_layout()
gu.axletters(ax,plt,0.035,0.93,FontColor=meta['Graphics']['gp']['cla'],LetterStyle=meta['Graphics']['Modelling']['AxesLetterStyle'],FontWeight=meta['Graphics']['Modelling']['AxesFontWeight'])
gu.PrintFig(meta['Graphics']['Print Figure Path'] + '\\AreaAffected','png',900)

#%% Graphic settings
t0=1850
t1=2150
cNam='Interior'
#cNam='Coast'

#%% Volume
plt.close('all')
td={'Year':np.array([2030,2050,2100,2145])}
udem.PlotVolumeMerchLive(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='upper right',FigSize=[12,6],TextDelta=td,FillDelta='On')

#%% Pools
plt.close('all')
td={'Year':np.array([2030,2050,2100,2145]),'Units':'Actual'}
udem.PlotPools(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='lower right',FigSize=[16,14],TextDelta=td)

#%% Fluxes
plt.close('all')
td={'Year':np.array([2100]),'Units':'Actual'}
udem.PlotFluxes(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='lower right',FigSize=[16,14],TextDelta=td)

#%% Delta GHG balance
plt.close('all')
udem.PlotDeltaGHGB(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='upper right',FigSize=[16,10])

#%% Schematic GHG balance
plt.close('all')
t0=meta[pNam]['Project']['Year Project']
t1=meta[pNam]['Project']['Year Project']+30
ax=udem.PlotSchematicBalance(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

#%%
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
iT=np.where( (tv>=2025) & (tv<=2150) )[0]
ufcs.Area_DisturbedAndManaged(meta,pNam,mos,1,1,iT,iPS,iSS,iYS,multi=1)

#%% Plot carbon pools (custom)
cnam='Interior'
operS='Mean'
t0=2010
t1=2150
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
iT=np.where((tv>=t0) & (tv<=t1))[0]
iB=mos[pNam]['Delta'][cnam]['iB']
iP=mos[pNam]['Delta'][cnam]['iP']
td={'Year':np.array([2050,2075,2100,2125])}

plt.close('all'); fig,ax=plt.subplots(3,2,figsize=gu.cm2inch(16,10))
v='C_Biomass'
y1=mos[pNam]['Scenarios'][iB][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
y2=mos[pNam]['Scenarios'][iP][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
ymx=1.2*np.max([np.max(y1),np.max(y2)])
ax[0,0].fill_between(tv[iT],y1,y2,color=[0.8,1,0.3],alpha=0.5,linewidth=0)
ax[0,0].plot(tv[iT],y1,'-',color=[0,0,0],lw=1.25,label='Baseline')
ax[0,0].plot(tv[iT],y2,'--',color=[0.6,0.9,0],lw=1.25,label='Action')
ax[0,0].legend(loc='lower right',frameon=False,facecolor=None)
be_d=(y2-y1)/y1*100
for yr in td['Year']:
	iT2=np.where(tv[iT]==yr)[0]
	if be_d[iT2]>0:
		tx='+' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	elif np.isnan(be_d[iT2])==True:
		tx=''
	else:
		tx='-' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	ax[0,0].text(tv[iT][iT2],1.05*y2[iT2],tx,fontsize=7,fontweight='bold',ha='center',color=[0.3,0.45,0])
ax[0,0].set(ylabel=r'Biomass (tC/ha)',xlabel=r'Time, years',ylim=[0,ymx],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[0,0].yaxis.set_ticks_position('both'); ax[0,0].xaxis.set_ticks_position('both'); ax[0,0].tick_params(length=meta['Graphics']['gp']['tickl'])

v='C_DeadWood'
y1=mos[pNam]['Scenarios'][iB][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
y2=mos[pNam]['Scenarios'][iP][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
ymx=1.2*np.max([np.max(y1),np.max(y2)])
ax[0,1].fill_between(tv[iT],y1,y2,color=[0.8,1,0.3],alpha=0.5,linewidth=0)
ax[0,1].plot(tv[iT],y1,'-',color=[0,0,0],lw=1.25,label='Baseline')
ax[0,1].plot(tv[iT],y2,'--',color=[0.6,0.9,0],lw=1.25,label='Action')
be_d=(y2-y1)/y1*100
for yr in td['Year']:
	iT2=np.where(tv[iT]==yr)[0]
	if be_d[iT2]>0:
		tx='+' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	elif np.isnan(be_d[iT2])==True:
		tx=''
	else:
		tx='-' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	ax[0,1].text(tv[iT][iT2],1.05*y2[iT2],tx,fontsize=7,fontweight='bold',ha='center',color=[0.3,0.45,0])
ax[0,1].set(ylabel=r'Dead wood (tC/ha)',xlabel=r'Time, years',ylim=[0,ymx],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[0,1].yaxis.set_ticks_position('both'); ax[0,1].xaxis.set_ticks_position('both'); ax[0,1].tick_params(length=meta['Graphics']['gp']['tickl'])

v='C_Litter'
y1=mos[pNam]['Scenarios'][iB][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
y2=mos[pNam]['Scenarios'][iP][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
ymx=1.2*np.max([np.max(y1),np.max(y2)])
ax[1,0].fill_between(tv[iT],y1,y2,color=[0.8,1,0.3],alpha=0.5,linewidth=0)
ax[1,0].plot(tv[iT],y1,'-',color=[0,0,0],lw=1.25,label='Baseline')
ax[1,0].plot(tv[iT],y2,'--',color=[0.6,0.9,0],lw=1.25,label='Action')
be_d=(y2-y1)/y1*100
for yr in td['Year']:
	iT2=np.where(tv[iT]==yr)[0]
	if be_d[iT2]>0:
		tx='+' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	elif np.isnan(be_d[iT2])==True:
		tx=''
	else:
		tx='-' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	ax[1,0].text(tv[iT][iT2],1.05*y2[iT2],tx,fontsize=7,fontweight='bold',ha='center',color=[0.3,0.45,0])
ax[1,0].set(ylabel=r'Litter (tC/ha)',xlabel=r'Time, years',ylim=[0,ymx],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[1,0].yaxis.set_ticks_position('both'); ax[1,0].xaxis.set_ticks_position('both'); ax[1,0].tick_params(length=meta['Graphics']['gp']['tickl'])

v='C_Soil'
y1=mos[pNam]['Scenarios'][iB][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
y2=mos[pNam]['Scenarios'][iP][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
ymx=1.2*np.max([np.max(y1),np.max(y2)])
ax[1,1].fill_between(tv[iT],y1,y2,color=[0.8,1,0.3],alpha=0.5,linewidth=0)
ax[1,1].plot(tv[iT],y1,'-',color=[0,0,0],lw=1.25,label='Baseline')
ax[1,1].plot(tv[iT],y2,'--',color=[0.6,0.9,0],lw=1.25,label='Action')
be_d=(y2-y1)/y1*100
for yr in td['Year']:
	iT2=np.where(tv[iT]==yr)[0]
	if be_d[iT2]>0:
		tx='+' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	elif np.isnan(be_d[iT2])==True:
		tx=''
	else:
		tx='-' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	ax[1,1].text(tv[iT][iT2],1.05*y2[iT2],tx,fontsize=7,fontweight='bold',ha='center',color=[0.3,0.45,0])
ax[1,1].set(ylabel=r'Soil (tC/ha)',xlabel=r'Time, years',ylim=[0,ymx],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[1,1].yaxis.set_ticks_position('both'); ax[1,1].xaxis.set_ticks_position('both'); ax[1,1].tick_params(length=meta['Graphics']['gp']['tickl'])

v='C_HWP'
y1=mos[pNam]['Scenarios'][iB][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
y2=mos[pNam]['Scenarios'][iP][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
ymx=1.2*np.max([np.max(y1),np.max(y2)])
ax[2,0].fill_between(tv[iT],y1,y2,color=[0.8,1,0.3],alpha=0.5,linewidth=0)
ax[2,0].plot(tv[iT],y1,'-',color=[0,0,0],lw=1.25,label='Baseline')
ax[2,0].plot(tv[iT],y2,'--',color=[0.6,0.9,0],lw=1.25,label='Action')
be_d=(y2-y1)/y1*100
for yr in td['Year']:
	iT2=np.where(tv[iT]==yr)[0]
	if be_d[iT2]>0:
		tx='+' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	elif np.isnan(be_d[iT2])==True:
		tx=''
	else:
		tx='-' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	ax[2,0].text(tv[iT][iT2],1.05*y2[iT2],tx,fontsize=7,fontweight='bold',ha='center',color=[0.3,0.45,0])
ax[2,0].set(ylabel=r'Products (tC/ha)',xlabel=r'Time, years',ylim=[0,ymx],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[2,0].yaxis.set_ticks_position('both'); ax[2,0].xaxis.set_ticks_position('both'); ax[2,0].tick_params(length=meta['Graphics']['gp']['tickl'])

v='C_Geological'
y1=mos[pNam]['Scenarios'][iB][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
y2=mos[pNam]['Scenarios'][iP][operS][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
ymx=1.2*np.max([np.min(y1),np.min(y2)])
ax[2,1].fill_between(tv[iT],y1,y2,color=[0.8,1,0.3],alpha=0.5,linewidth=0)
ax[2,1].plot(tv[iT],y1,'-',color=[0,0,0],lw=1.25,label='Baseline')
ax[2,1].plot(tv[iT],y2,'--',color=[0.6,0.9,0],lw=1.25,label='Action')
be_d=(y2-y1)/y1*100
for yr in td['Year']:
	iT2=np.where(tv[iT]==yr)[0]
	if be_d[iT2]>0:
		tx='+' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	elif np.isnan(be_d[iT2])==True:
		tx=''
	else:
		tx='-' + str(np.round(be_d[iT2[0]],decimals=1)) + '%'
	ax[2,1].text(tv[iT][iT2],1.05*y2[iT2],tx,fontsize=7,fontweight='bold',ha='center',color=[0.3,0.45,0])
ax[2,1].set(ylabel=r'Geological deposits (tC/ha)',xlabel=r'Time, years',ylim=[ymx,0],xlim=[np.min(tv[iT]),np.max(tv[iT])]);
ax[2,1].yaxis.set_ticks_position('both'); ax[2,1].xaxis.set_ticks_position('both'); ax[2,1].tick_params(length=meta['Graphics']['gp']['tickl'])

#ax[0].annotate('Harvest',xy=(meta[pNam]['Project']['Year Project']-36,1000),xytext=(meta[pNam]['Project']['Year Project']-36,1200),arrowprops={'color':'black','arrowstyle':'->'},ha='center');
gu.axletters(ax,plt,0.035,0.88,FontColor=meta['Graphics']['gp']['cla'],LetterStyle=meta['Graphics']['Modelling']['AxesLetterStyle'],FontWeight=meta['Graphics']['Modelling']['AxesFontWeight'])
plt.tight_layout()
gu.PrintFig(meta['Graphics']['Print Figure Path'] + '\\SummaryCarbonPoolsTS','png',900)


#%%

r_disc=0.04
t_disc=tv-meta[pNam]['Project']['Year Project']
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
iT=np.where( (tv>=2022) )[0]
iT0=np.where( (tv[iT]==meta[pNam]['Project']['Year Project']+10) )[0]

cnam='Interior'
#vL=['E_AGHGB_WOSub','E_AGHGB_WHSub','Revenue Net','Revenue Gross','Cost Total']
vL=['E_AGHGB_WOSub','Cost Total','Revenue Gross','Revenue Net']
d={}
for v in vL:
	d[v]=np.cumsum(mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])[iT0[0]]
d['Upfront MV']=-60.20/d['E_AGHGB_WOSub']
d['Complete MV']=d['Cost Total']/d['E_AGHGB_WOSub']
for v in vL:
	d[v + '_disc']=np.cumsum(mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS]/((1+r_disc)**t_disc[iT]))[iT0[0]]
d['Upfront MV_disc']=-60.20/d['E_AGHGB_WOSub_disc']
d['Complete MV_disc']=d['Cost Total_disc']/d['E_AGHGB_WOSub_disc']
d

cnam='Coast'
#vL=['E_AGHGB_WOSub','E_AGHGB_WHSub','Revenue Net','Revenue Gross','Cost Total']
vL=['E_AGHGB_WOSub','Cost Total','Revenue Gross','Revenue Net']
d={}
for v in vL:
	d[v]=np.cumsum(mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])[iT0[0]]
d['Upfront MV']=-9.98/d['E_AGHGB_WOSub']
d['Complete MV']=d['Cost Total']/d['E_AGHGB_WOSub']
for v in vL:
	d[v + '_disc']=np.cumsum(mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS]/((1+r_disc)**t_disc[iT]))[iT0[0]]
d['Upfront MV_disc']=-9.98/d['E_AGHGB_WOSub_disc']
d['Complete MV_disc']=d['Cost Total_disc']/d['E_AGHGB_WOSub_disc']
d

#%%

def MitigationSummary(meta,pNam,mos):
	r_disc=0.03
	t_disc=tv-meta[pNam]['Project']['Year Project']

	tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
	iT=np.where( (tv>=2022) & (tv<=meta[pNam]['Project']['Year Project']+100) )[0]

	#vL=['E_AGHGB_WOSub','E_AGHGB_WHSub','Revenue Net','Revenue Gross','Cost Total']
	vL=['E_AGHGB_WOSub','Revenue Net','Revenue Gross','Cost Total']
	d={}
	for cnam in mos[pNam]['Delta'].keys():
		d[cnam]={}
		for v in vL:
			d[cnam][v]={}
			d[cnam][v]['ann']=mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS]
			d[cnam][v]['ann disc']=mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS]/((1+r_disc)**t_disc[iT])
			d[cnam][v]['cumu']=np.cumsum(mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])
			d[cnam][v]['cumu disc']=np.cumsum(mos[pNam]['Delta'][cnam]['ByStrata']['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS]/((1+r_disc)**t_disc[iT]))
			print(d[cnam][v]['cumu'][-1])
			#print(d[cnam][v]['cumu disc'][-1])

	cnam='Interior'

	plt.close('all');
	plt.plot(tv[iT],-d[cnam]['Cost Total']['cumu']/1000,'r-')
	plt.plot(tv[iT],d[cnam]['Revenue Gross']['cumu']/1000,'b-')
	plt.plot(tv[iT],d[cnam]['Revenue Net']['cumu']/1000,'g-')

	plt.close('all');
	plt.plot(-d[cnam]['Cost Total']['cumu'],d[cnam]['E_AGHGB_WHSub']['cumu'],'b--')
	plt.plot(d[cnam]['Revenue Net']['cumu'],d[cnam]['E_AGHGB_WHSub']['cumu'],'g-')

	plt.plot(-d[cnam]['Cost Total']['cumu disc'],d[cnam]['E_AGHGB_WHSub']['cumu disc'],'b--')
	plt.plot(d[cnam]['Revenue Net']['cumu disc'],d[cnam]['E_AGHGB_WHSub']['cumu disc'],'c-')

	#plt.close('all');
	plt.plot(d[cnam]['Revenue Net']['cumu'],d[cnam]['E_AGHGB_WHSub']['cumu'],'g-')
	plt.plot(d[cnam]['Revenue Net']['cumu disc'],d[cnam]['E_AGHGB_WHSub']['cumu disc'],'c-')


	plt.close('all');
	plt.plot(tv[iT],d[cnam]['E_AGHGB_WOSub']['cumu'],'g-')
	plt.plot(tv[iT],d[cnam]['E_AGHGB_WOSub']['cumu disc'],'c-')

	np.zeros((6,2))
	#v='E_AGHGB_WOSub'
	
	E0=mos[pNam]['Scenarios'][0]['Mean'][v]['Ensemble Mean'][:,iPS,iSS,iYS]
	E1=mos[pNam]['Scenarios'][1]['Mean'][v]['Ensemble Mean'][:,iPS,iSS,iYS]
	Ed0=mos[pNam]['Scenarios'][0]['Mean'][v]['Ensemble Mean'][:,iPS,iSS,iYS]/((1+r_disc)**t_disc)
	Ed1=mos[pNam]['Scenarios'][1]['Mean'][v]['Ensemble Mean'][:,iPS,iSS,iYS]/((1+r_disc)**t_disc)
	Ea=np.cumsum(E1-E0)
	Ed=np.cumsum(Ed1-Ed0)
	return

plt.close('all');
plt.plot(tv,Ea,'b-')
plt.plot(tv,Ed,'r--')




iT=np.where( (tv>=2023) & (tv<=2030) )[0]
mu1=np.sum()
mu2=np.sum(mos[pNam]['Scenarios'][1]['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])/((1+r_disc)**t_disc)
d[0,0]=mu2-mu1
#print((mu2-mu1)/mu1*100)

iT=np.where( (tv>=2023) & (tv<=2050) )[0]
mu1=np.sum(mos[pNam]['Scenarios'][0]['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])/((1+r_disc)**t_disc)
mu2=np.sum(mos[pNam]['Scenarios'][1]['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])/((1+r_disc)**t_disc)
d[1,0]=mu2-mu1
#print((mu2-mu1)/mu1*100)

iT=np.where( (tv>=2023) & (tv<=2070) )[0]
mu1=np.sum(mos[pNam]['Scenarios'][0]['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])/((1+r_disc)**t_disc)
mu2=np.sum(mos[pNam]['Scenarios'][1]['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])/((1+r_disc)**t_disc)
d[2,0]=mu2-mu1

iT=np.where( (tv>=2023) & (tv<=2070) )[0]
mu1=np.sum(mos[pNam]['Scenarios'][0]['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])/((1+r_disc)**t_disc)
mu2=np.sum(mos[pNam]['Scenarios'][1]['Mean'][v]['Ensemble Mean'][iT,iPS,iSS,iYS])/((1+r_disc)**t_disc)
d[3,0]=mu2-mu1
#print((mu2-mu1)/mu1*100)

plt.plot(d[:,0])

#%%

#%% Area

iT=np.where(tv>2023)[0]
yF=np.cumsum(mos[pNam]['Scenarios'][1]['Mean']['Area_Wildfire']['Ensemble Mean'][iT,0,0,0])*100#/meta[pNam]['Project']['N Stand']*100
yB=np.cumsum(mos[pNam]['Scenarios'][1]['Mean']['Area_Mountain Pine Beetle']['Ensemble Mean'][iT,0,0,0])*100#/meta[pNam]['Project']['N Stand']*100
yP=np.cumsum((mos[pNam]['Scenarios'][1]['Mean']['Area_Disease Root']['Ensemble Mean'][iT,0,0,0]+
	mos[pNam]['Scenarios'][1]['Mean']['Area_Disease Stem']['Ensemble Mean'][iT,0,0,0]+
	mos[pNam]['Scenarios'][1]['Mean']['Area_Disease Foliage']['Ensemble Mean'][iT,0,0,0]))*100#/meta[pNam]['Project']['N Stand']*100
yH=np.cumsum(mos[pNam]['Scenarios'][1]['Mean']['Area_Harvest']['Ensemble Mean'][iT,0,0,0])*100#/meta[pNam]['Project']['N Stand']*100

cl=np.array([[0,0,1],[0,1,1],[1,0,0],[0.5,0,0]])
plt.close('all')
plt.fill_between(tv[iT],np.zeros(iT.size),yF,color=cl[0,:])
plt.fill_between(tv[iT],yF,yF+yB,color=cl[1,:])
plt.fill_between(tv[iT],yF+yB,yF+yB+yP,color=cl[2,:])
plt.fill_between(tv[iT],yF+yB+yP,yF+yB+yP+yH,color=cl[3,:])