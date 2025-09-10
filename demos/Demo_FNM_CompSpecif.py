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
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Configure project
meta=u1ha.Init()
pNam='Demo_NM_CompSpecs'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'C:\Data\BCFCS\Demo_NM_CompSpecs'
meta=cbu.ImportProjectConfig(meta,pNam)
meta['Graphics']['Print Figures']='On'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\Demo\Demo Nutrient Management\CompareSpecifications'
    
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
#cbu.Calc_MOS_Area(meta,pNam)
cbu.Calc_MOS_MortByAgent(meta,pNam)

#%% Import results
pNam='Demo_NM_CompSpecs'
meta=gu.ipickle(r'C:\Data\BCFCS\Demo_NM_CompSpecs\Inputs\Metadata.pkl')
mos=cbu.Import_MOS_ByScnAndStrata_GHGEcon(meta,pNam)
mos[pNam]['Delta']={}
mos[pNam]['Delta']['NGS']={'iB':0,'iP':1}
mos[pNam]['Delta']['NGT']={'iB':0,'iP':2}
mos[pNam]['Delta']['NGT+T']={'iB':0,'iP':3}
mos[pNam]['Delta']['NGT+T+D']={'iB':0,'iP':4}
mos=cbu.Import_MOS_ByScnComparisonAndStrata(meta,pNam,mos)

#%% Summarize impact on pools
udem.NA_CompareSpecifications_ChangeInPools(meta,pNam,mos)

#%% Graphics
t0=1900
t1=2100
plt.close('all')
udem.PlotPools(meta,mos,pNam,cnam='NGT+T+D',operSpace='Mean',t0=t0,t1=t1,ScenarioLabels=['Baseline','Action'],LegendLoc='upper right')
udem.PlotFluxes(meta,mos,pNam,cnam='NGT+T+D',operSpace='Mean',t0=t0,t1=t1,ScenarioLabels=['Baseline','Action'],LegendLoc='lower left')




