'''
USED TO GENERATE BACK OF ENVELOPE VOLUME STIMULUS FOR JIM AND LEITH
'''

#%% Import modules
import numpy as np
import matplotlib.pyplot as plt
import time
import warnings
import fcgadgets.macgyver.util_general as gu
import fcgadgets.macgyver.util_inventory as uinv
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun as cbr
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.macgyver.util_demo as udem
import fcgadgets.macgyver.util_nm as unm
import fcgadgets.gaia.gaia_util as gaia
import fcexplore.field_plots.Processing.fp_util as ufp
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Configure project
meta=u1ha.Init()
pNam='Demo_FNM_BySpecies'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'D:\Modelling Projects\Demo_FNM_BySpecies'
meta=cbu.ImportProjectConfig(meta,pNam)
meta['Graphics']['Print Figures']='On'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\Demo\Demo_FNM_BySpecies'

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
pNam='Demo_FNM_BySpecies'
pth=r'D:\Modelling Projects\Demo_FNM_BySpecies\Inputs\Metadata.pkl'
meta=gu.ipickle(pth)
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
mos=cbu.Import_MOS_ByScnAndStrata_GHGEcon(meta,pNam)
mos[pNam]['Delta']={}
mos[pNam]['Delta']['FDC']={'iB':0,'iP':1}
mos[pNam]['Delta']['HW']={'iB':2,'iP':3}
mos[pNam]['Delta']['CW']={'iB':4,'iP':5}
mos[pNam]['Delta']['PL']={'iB':6,'iP':7}
mos[pNam]['Delta']['SW']={'iB':8,'iP':9}
mos[pNam]['Delta']['SS']={'iB':10,'iP':11}
mos=cbu.Import_MOS_ByScnComparisonAndStrata(meta,pNam,mos)
#mos=gaia.Calc_RF_FAIR(meta,pNam,mos)

# Save for BC-FCS
#gu.opickle(meta['Paths'][pNam]['Data'] + '\\Outputs\\MOS_GHGB.pkl',mos)

#%% Comparison with CBM
#uqa.QA_BenchmarkCBM_FNM(meta,pNam,mos)

#%% Export tables for each scenario
tbs=udem.Export_Summary_Tables(meta,pNam,mos)

#%%
for cNam in tbs['Scenario Comparison'].keys():
	print(tbs['Scenario Comparison'][cNam]['Mean_in_t+10']['V_MerchTotal'])

#%% Manually generate excel from TIPSY output file
dGY=gu.ReadExcel(r'D:\Modelling Projects\Demo_FNM_BySpecies\Inputs\GrowthCurvesTIPSY_Output.xlsx',sheet_name='Sheet1',skiprows=0)

id=9
plt.close('all')
ind1=np.where( (dGY['Scn']==id) & (dGY['GC']==2) )[0]
#plt.plot(dGY['VolTot0'][ind1],'b-')
ind2=np.where( (dGY['Scn']==id+1) & (dGY['GC']==2) )[0]
#plt.plot(dGY['VolTot0'][ind2],'r--')
plt.plot(dGY['VolMerch125'][ind2]-dGY['VolMerch125'][ind1],'k-')
plt.plot(dGY['VolMerch175'][ind2]-dGY['VolMerch175'][ind1],'k-')

#%% Save to change tracker
#udem.Record_In_ChangeTrackerDB(meta,pNam,mos,tbs,['Coast No Harvest','Coast With Harvest'])

#%% Graphic settings
t0=1950
t1=2150
cNam='Coast No Harvest'
#cNam='Coast With Harvest'

#%% Volume
plt.close('all')
td={'Year':np.array([2030,2050,2100,2145])}
udem.PlotVolumeMerchLive(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='upper right',FigSize=[16,6],TextDelta=td,FillDelta='On')

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
udem.PlotDeltaGHGB(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],
				   LegendLoc='lower right',FigSize=[16,10])

#%% Schematic GHG balance
plt.close('all')
t0=meta[pNam]['Project']['Year Project']
t1=meta[pNam]['Project']['Year Project']+50
ax=udem.PlotSchematicBalance(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

#%% Export tables
df=udem.ExportTableDelta(meta,pNam,mos,cnam=['Coast With Harvest'],table_name='Econ',oper='Sum',t0=2020,t1=2100,units='Actual',save='On')
df=udem.ExportTableDelta(meta,pNam,mos,table_name='ScnComp1',oper='Sum',t0=t0,t1=t1,units='Actual',cnam=['Coast No Harvest','Interior No Harvest'])
df=udem.ExportTableDelta(meta,pNam,mos,table_name='ScnComp1',oper='Sum',t0=t0,t1=t1,units='Actual',save='On')
df=udem.ExportTableDelta(meta,pNam,mos,table_name='ScnComp1',oper='Sum',t0=t0,t1=t1,units='Actual',save='On')
df=udem.ExportTableDelta(meta,pNam,mos,table_name='ScnComp1',oper='Mean',t0=t0,t1=t1,units='Relative')
df=udem.ExportTableDelta(meta,pNam,mos,table_name='ScnComp1',oper='Mean',t0=t0,t1=t1,units='Relative')

vL=['C_Biomass_Tot','C_DeadWood_Tot','C_Litter_Tot','C_Soil_Tot']
tL=[meta[pNam]['Project']['Year Project'],meta[pNam]['Project']['Year Project']+10]
df=udem.ExportTableDelta(meta,pNam,mos,table_name='ScnComp1',oper='mean',tL,Units='Relative',Variables=vL)

#%% Graphics
t0=1900
t1=2100
plt.close('all')
udem.PlotPools(meta,mos,pNam,cnam='Coast With Harvest',operSpace='Mean',t0=t0,t1=t1,ScenarioLabels=['Baseline','Action'],LegendLoc='upper right')
udem.PlotPools(meta,mos,pNam,cnam='Interior With Harvest',operSpace='Mean',t0=t0,t1=t1,ScenarioLabels=['Baseline','Action'],LegendLoc='upper right')
udem.PlotFluxes(meta,mos,pNam,cnam='Interior With Harvest',operSpace='Mean',t0=t0,t1=t1,ScenarioLabels=['Baseline','Action'],LegendLoc='lower left')
udem.PlotDeltaNEP(meta,mos,pNam,cnam='Coast No Harvest',operSpace='Mean',t0=t0,t1=t1)
udem.PlotDeltaGHGB(meta,mos,pNam,cnam='Coast No Harvest',operSpace='Mean',t0=t0,t1=t1)
udem.PlotSchematicAtmoGHGBal(meta,pNam,mos,cnam='Coast With Harvest',operSpace='Mean',t0=meta[pNam]['Project']['Year Project'],t1=meta[pNam]['Project']['Year Project']+30)
udem.PlotCashflow(meta,pNam,mos,cnam='Coast With Harvest',operSpace='Mean',t0=1950,t1=2100)

#%% Volume
udem.PlotVolumeMerchLive(meta,pNam,mos,cnam='Coast With Harvest',operSpace='Mean',t0=1900,t1=2100)

#%% Cashflow

vL=['C_Biomass','C_DeadWood','C_Litter','C_Soil','C_Forest','C_HWP','C_Geological']
df=udem.ExportTableScenariosAndDelta(meta,pNam,mos,
                                     cNam=['NMC1'],
                                     table_name='Pools',
                                     operTime='Mean',
                                     operSpace='Sum',
                                     t0=2021,t1=2030,
                                     iPS=0,iSS=0,iYS=0,
                                     Units='Actual',
                                     multi=1e-6,
                                     Save='Off',
                                     variables=vL)

#%%
#ufcs.AllVariableTimeSeries(meta,pNam,mos,tv,0,iT)

#%% Plot GHG benefit With C.I.s
udem.NA_CumulativeGHGBenefit_WithCI(meta,pNam,mos,t0=2010,t1=2080,Error='50%',LegendPosition='upper right')

#%% Nitrogen use efficiency
df=udem.NA_CalcNUE(meta,pNam,mos,table_name='ScnComp1',t0=meta[pNam]['Project']['Year Project'],t1=meta[pNam]['Project']['Year Project']+10,cnam=['Coast No Harvest','Interior No Harvest'])


#%% Benchmark economics

d={}
tNam='Sum_t-5_to_t+100'
for cNam in tbs['Scenario Comparison'].keys():
	d[cNam]={}
	d[cNam]['Cost (CAD/m3)']=np.round(tbs['Scenario Comparison'][cNam][tNam]['Cost Total']/tbs['Scenario Comparison'][cNam][tNam]['V_ToMill_MerchTotal'],decimals=2)
	d[cNam]['Gross revenue (CAD/m3)']=np.round(tbs['Scenario Comparison'][cNam][tNam]['Revenue Gross']/tbs['Scenario Comparison'][cNam][tNam]['V_ToMill_MerchTotal'],decimals=2)
	d[cNam]['Net revenue (CAD/m3)']=np.round(tbs['Scenario Comparison'][cNam][tNam]['Revenue Net']/tbs['Scenario Comparison'][cNam][tNam]['V_ToMill_MerchTotal'],decimals=2)
df=pd.DataFrame.from_dict(d)
display(df)

#%%