#%% Import modules
import numpy as np
import matplotlib.pyplot as plt
import warnings
import fcgadgets.macgyver.util_general as gu
import fcgadgets.macgyver.util_inventory as uinv
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun as cbr
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.macgyver.util_demo as udem
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Configure project
meta=u1ha.Init()
pNam='Demo_RefSalvMPB'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'C:\Data\BCFCS\Demo_RefSalvMPB'
meta=cbu.ImportProjectConfig(meta,pNam)
meta['Graphics']['Print Figures']='On'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\Demo\Demo_RefSalvMPB'

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
pNam='Demo_RefSalvMPB'
pth=r'C:\Data\BCFCS\Demo_RefSalvMPB\Inputs\Metadata.pkl'
meta=gu.ipickle(pth)
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
mos=cbu.Import_MOS_ByScnAndStrata_GHGEcon(meta,pNam)
mos[pNam]['Delta']={}
mos[pNam]['Delta']['Delta1']={'iB':0,'iP':1}
mos[pNam]['Delta']['Delta2']={'iB':0,'iP':2}
mos=cbu.Import_MOS_ByScnComparisonAndStrata(meta,pNam,mos)
mos=cbu.Import_MOS_ByScnAndStrata_Area(meta,pNam,mos)
iPS=0; iSS=0; iYS=0
cNam='Delta1'

#%% Export tables for each scenario

# Use this to estimate delta at year 50
t0=meta[pNam]['Project']['Year Project']
t1=meta[pNam]['Project']['Year Project']+50
df=udem.ExportTableByScenario(meta,pNam,mos,table_name='Mean Annual Delta at 50 years',operTime='Mean',t0=t0,t1=t1)

# Use this to estimate delta at year 100
t0=meta[pNam]['Project']['Year Project']
t1=meta[pNam]['Project']['Year Project']+100
df=udem.ExportTableByScenario(meta,pNam,mos,table_name='Mean Annual Delta at 100 years',operTime='Mean',t0=t0,t1=t1)
df=udem.ExportTableByScenario(meta,pNam,mos,table_name='Sum Annual Delta at 100 years',operTime='Sum',t0=t0,t1=t1)

# Use this to estimate delta at year 2050
t0=meta[pNam]['Project']['Year Project']
t1=2050
df=udem.ExportTableByScenario(meta,pNam,mos,table_name='Sum Delta at 2050',operTime='Sum',t0=t0,t1=t1)
df=udem.ExportTableByScenario(meta,pNam,mos,table_name='Mean Delta at 2050',operTime='Mean',t0=t0,t1=t1)

#%% Plot volume
t0=2000
t1=2150
plt.close('all')
td={'Year':np.array([2050,2075,2100,2125])}
udem.PlotVolumeMerchLive(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1,operSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='upper right',FigSize=[12,6],TextDelta=td,FillDelta='On')

#%% Pools
t0=2000
t1=2150
plt.close('all')
td={'Year':np.array([2030,2050,2100]),'Units':'Actual'}
udem.PlotPools(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,operSpace='Mean',ScenarioLabels=['Baseline','Action'],LegendLoc='lower right',FigSize=[16,13],TextDelta=td)

#%% Fluxes
t0=2000
t1=2150
plt.close('all')
td={'Year':np.array([2030,2050,2100]),'Units':'Actual'}
udem.PlotFluxes(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,operSpace='Mean',ScenarioLabels=['Baseline','Action'],LegendLoc='lower right',FigSize=[16,13],TextDelta=td)

#%% Biomass fluxes
t0=2000
t1=2150
udem.PlotFluxesBiomass(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,operSpace='Mean')

#%% Age
udem.PlotAge(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,operSpace='Mean',ScenarioLabels=['Baseline','Action'],LegendLoc='lower right',FigSize=[16,13])

#%%
t0=2000
t1=2150
plt.close('all')
td={'Year':np.array([2030,2050,2100])}
udem.PlotDeltaGHGB(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,operSpace='Mean',ScenarioLabels=['Baseline','Action'],yLimPad=1.5,FigSize=[16,9])

#%%
t0=meta[pNam]['Project']['Year Project']
t1=meta[pNam]['Project']['Year Project']+50
udem.PlotSchematicAtmoGHGBal(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

#%%
udem.PlotDeltaNEE(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,operSpace='Mean',)

#%%
udem.PlotCashflow(meta,pNam,mos,cNam=cNam,t0=1950,t1=2100)

#%%
plt.close('all')
plt.plot(tv,mos[pNam]['Delta'][cnam]['ByStrata']['Mean']['E_AGHGB_WSub_cumu_from_tref']['Ensemble Mean'][:,iPS,iSS,iYS],'b-')
plt.plot(tv,mos[pNam]['Delta'][cnam]['ByStrata']['Mean']['E_AGHGB_WOSub_cumu_from_tref']['Ensemble Mean'][:,iPS,iSS,iYS],'r--')

#%%
udem.PlotDeltaNEE(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1)

#%%
udem.PlotDeltaGHGB(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1)
#udem.PlotSchematicAtmoGHGBal(meta,pNam,mos,cnam='Coast With Harvest',t0=meta[pNam]['Project']['Year Project'],t1=meta[pNam]['Project']['Year Project']+30)

#%% Schematic diagram
t0=2000
t1=2150
udem.PlotSchematicAtmoGHGBal(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

#%%
t0=meta[pNam]['Project']['Year Project']-1
t1=meta[pNam]['Project']['Year Project']+100
udem.MitigationSummary(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

