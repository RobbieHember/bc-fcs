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
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Configure project
meta=u1ha.Init()
pNam='Demo_FNM_FluxTowerComp'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'D:\Modelling Projects\Demo_FNM_FluxTowerComp'
meta=cbu.ImportProjectConfig(meta,pNam)
meta['Graphics']['Print Figures']='On'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\Demo\Demo_FNM_FluxTowerComp'

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
pNam='Demo_FNM_FluxTowerComp'
pth=r'D:\Modelling Projects\Demo_FNM_FluxTowerComp\Inputs\Metadata.pkl'
meta=gu.ipickle(pth)
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
mos=cbu.Import_MOS_ByScnAndStrata_GHGEcon(meta,pNam)
#mos[pNam]['Delta']={}
#mos[pNam]['Delta']['Coast No Harvest']={'iB':0,'iP':1}
#mos=cbu.Import_MOS_ByScnComparisonAndStrata(meta,pNam,mos)
#mos=gaia.Calc_RF_FAIR(meta,pNam,mos)
#gu.opickle(meta['Paths'][pNam]['Data'] + '\\Outputs\\MOS_GHGB.pkl',mos)

# Import flux tower observations
obs=gu.ReadExcel(r'C:\Data\Eddy Covariance\DF49\DF NEP chrono Combined.xlsx')
iObs=np.where(obs['Site']!='HDF11')[0]

#%% Plot

plt.close('all'); fig,ax=plt.subplots(1,figsize=gu.cm2inch(12,8)); lw=1.25
ax.plot([-10,100],[0,0],'-',linewidth=0.75,color='k')
# Baseline
ax.plot(tv-2000,-mos[pNam]['Scenarios'][0]['Mean']['E_Domestic_ForestSector_NEE']['Ensemble Mean'][:,0,0,0]/3.667,'-o',ms=2,color=(0.83,0.83,0.83),linewidth=lw,label='Baseline model (SI = 30m)')
# Add observations
ax.plot(obs['Age'][iObs],obs['NEP'][iObs]/100,'ko',markersize=4,markerfacecolor='w',markeredgecolor='k',linewidth=0.5,label='Flux tower observations')

t0=2000 # HDF00
it0=np.where( (tv>=2007-4) & (tv<=2007+6) )[0]
ax.plot(tv[it0]-t0,-mos[pNam]['Scenarios'][0]['Mean']['E_Domestic_ForestSector_NEE']['Ensemble Mean'][it0,0,0,0]/3.667,'-',color=(0.75,0.25,0),linewidth=lw,label='Baseline at age 7')
ax.plot(tv[it0]-t0,-mos[pNam]['Scenarios'][1]['Mean']['E_Domestic_ForestSector_NEE']['Ensemble Mean'][it0,0,0,0]/3.667,'--',color=(1,0.5,0),linewidth=lw,label='Application at age 7')

t0=1988 # HDF88
it0=np.where( (tv>=2007-4) & (tv<=2007+15) )[0]
ax.plot(tv[it0]-t0,-mos[pNam]['Scenarios'][2]['Mean']['E_Domestic_ForestSector_NEE']['Ensemble Mean'][it0,0,0,0]/3.667,'-',color=(0.45,0.1,0.5),linewidth=lw,label='Baseline at age 19')
ax.plot(tv[it0]-t0,-mos[pNam]['Scenarios'][3]['Mean']['E_Domestic_ForestSector_NEE']['Ensemble Mean'][it0,0,0,0]/3.667,'--',color=(0.7,0.2,1),linewidth=lw,label='Application at age 19')

t0=1949 # DF49
it0=np.where( (tv>=2007-10) & (tv<=2007+15) )[0]
ax.plot(tv[it0]-t0,-mos[pNam]['Scenarios'][4]['Mean']['E_Domestic_ForestSector_NEE']['Ensemble Mean'][it0,0,0,0]/3.667,'-',color=(0.3,0.45,0),linewidth=lw,label='Baseline at age 58')
ax.plot(tv[it0]-t0,-mos[pNam]['Scenarios'][5]['Mean']['E_Domestic_ForestSector_NEE']['Ensemble Mean'][it0,0,0,0]/3.667,'--',color=(0.6,0.9,0),linewidth=lw,label='Application at age 58')

ax.annotate('Harvest',xy=(0,2.75),xytext=(0,6),arrowprops={'color':'black','arrowstyle':'->'},ha='center');
ax.annotate('Application',xy=(6.25,-2),xytext=(6.25,1),arrowprops={'color':'black','arrowstyle':'->'},ha='center');
ax.annotate('Application',xy=(18.25,3),xytext=(18.25,7),arrowprops={'color':'black','arrowstyle':'->'},ha='center');
ax.annotate('Application',xy=(57.25,5.5),xytext=(57.25,8.25),arrowprops={'color':'black','arrowstyle':'->'},ha='center');
ax.legend(loc="lower right",frameon=False,facecolor='white');
ax.set(ylabel='Net ecosystem production (tC ha$^{-1}$ yr$^{-1}$)',xticks=np.arange(-10,120,10),xlabel='Time since disturbance, years',ylim=[-16,10],xlim=[-10,75])
ax.yaxis.set_ticks_position('both'); ax.xaxis.set_ticks_position('both');
ax.tick_params(length=2)
if meta['Graphics']['Print Figures']=='On':
	gu.PrintFig(meta['Graphics']['Print Figure Path'] + '\\NEP','png',900)

#%%


