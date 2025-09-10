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
import fcgadgets.macgyver.util_qa as uqa
import fcgadgets.macgyver.util_demo as udem
import fcexplore.field_plots.Processing.fp_util as ufp
import fcgadgets.gaia.gaia_util as gaia
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Configure project
meta=u1ha.Init()
pNam='Demo_Ref_Underplant'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'D:\Modelling Projects\Demo_Ref_Underplant'
meta=cbu.ImportProjectConfig(meta,pNam)
meta['Graphics']['Print Figures']='On'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\Demo\Demo_Ref_Underplant'

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
pNam='Demo_Ref_Underplant'
pth=r'D:\Modelling Projects\Demo_Ref_Underplant\Inputs\Metadata.pkl'
meta=gu.ipickle(pth)
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
mos=cbu.Import_MOS_ByScnAndStrata_GHGEcon(meta,pNam)
mos[pNam]['Delta']={}
mos[pNam]['Delta']['Interior SR Class A']={'iB':0,'iP':3}
mos[pNam]['Delta']['Interior NSR Class A']={'iB':1,'iP':3}
mos[pNam]['Delta']['Interior NSR Class B']={'iB':1,'iP':2}
mos=cbu.Import_MOS_ByScnComparisonAndStrata(meta,pNam,mos)
iPS=0; iSS=0; iYS=0

# Calculate radiative forcing with FAIR
#mos=gaia.Calc_RF_FAIR(meta,pNam,mos)

#%% Comparison with CBM (ProjectConfig for CBM comparison saved as seperate file)
uqa.QA_BenchmarkCBM_RefUnderplanting(meta,pNam,mos)

#%% Radiative forcing summary
scnC='Interior NSR Class A'

# Radiative forcing from Betts 2000
E=mos[pNam]['Delta'][scnC]['ByStrata']['Mean']['E_NAB']['Ensemble Mean'][:,iPS,iSS,iYS] # tCO2e/ha/year
E=E/3.667 # tC/ha/yr
E=E*1000 # kgC/ha/yr
E=E/10000 # kgC/m2/yr
E=E/(2.13*1e12) # ppm
RF_Betts00=5.35*np.log(1+E/360)*1e9*1e4 # nW m-2 ha-1

plt.close('all'); fig,ax=plt.subplots(1,figsize=gu.cm2inch(18,14))
y1=mos[pNam]['Scenarios'][0]['Mean']['RF_Biochem']['Ensemble Mean'][:,iPS,iSS,iYS]
ax.plot(tv,y1,'c-',lw=2,label='FAIR25')
y1=mos[pNam]['Scenarios'][1]['Mean']['RF_Biochem']['Ensemble Mean'][:,iPS,iSS,iYS]
ax.plot(tv,y1,'b-',lw=2,label='FAIR25')
y1=mos[pNam]['Scenarios'][3]['Mean']['RF_Biochem']['Ensemble Mean'][:,iPS,iSS,iYS]
ax.plot(tv,y1,'r--',lw=2,label='FAIR25')

plt.close('all'); fig,ax=plt.subplots(1,figsize=gu.cm2inch(18,14))
#y1=mos[pNam]['Scenarios'][1]['Mean']['E_NAB']['Ensemble Mean'][:,iPS,iSS,iYS]
y1=mos[pNam]['Scenarios'][1]['Mean']['E_CO2']['Ensemble Mean'][:,iPS,iSS,iYS]
ax.plot(tv,y1,'b-',lw=2,label='FAIR25')
y1=mos[pNam]['Scenarios'][1]['Mean']['RF_Biochem']['Ensemble Mean'][:,iPS,iSS,iYS]
ax.plot(tv,y1,'r--',lw=2,label='FAIR25')


plt.close('all'); fig,ax=plt.subplots(1,figsize=gu.cm2inch(18,14))
ax.plot(tv,np.cumsum(RF_Betts00),'b-',lw=2,label='Betts 2000')
y1=mos[pNam]['Delta'][scnC]['ByStrata']['Mean']['RF_Biochem']['Ensemble Mean'][:,iPS,iSS,iYS]
ax.plot(tv,y1,'g--',lw=2,label='FAIR25')
ax.set(xticks=np.arange(1800,2200,20),ylabel='Radiative forcing',xlabel='Time, years',xlim=[1880,2150])
ax.legend(loc='lower right',facecolor=[1,1,1],frameon=False)
ax.yaxis.set_ticks_position('both'); ax.xaxis.set_ticks_position('both'); ax.tick_params(length=meta['Graphics']['gp']['tickl'])

#v='RF_AlbedoSurfaceShortwave'
#y2=mos[pNam]['Delta'][scnC]['ByStrata']['Mean'][v]['Ensemble Mean'][:,iPS,iSS,iYS]
#plt.plot(tv,y2,'g--')
#plt.plot(tv,y1+y2,'k-.')
#plt.plot(tv,np.cumsum(RF),'r-',lw=2)

#%%
plt.close('all')
for rf in meta['Modules']['FAIR']['Forcings']:
	plt.plot(tv,mos[pNam]['Delta'][scnC]['ByStrata']['Mean']['RF_Biochem_' + rf]['Ensemble Mean'][:,iPS,iSS,iYS],'-',lw=2,label=rf)
plt.legend()


#%%
iP=3
plt.close('all'); fig,ax=plt.subplots(3,2,figsize=gu.cm2inch(18,14))

#ax[0,0].plot(tv,dCBM['Biomass S_ID-3'],'k-',color=meta['Graphics']['gp']['cl1'],label='CBM25')
ax[0,0].plot(tv,mos[pNam]['Scenarios'][iP]['Mean']['C_Biomass']['Ensemble Mean'][:,0,0,0],'k--',color=meta['Graphics']['gp']['cl2'],label='FCG25')
#ax[0,0].plot(tv-107,dCBM['Biomass S_ID-3'],'k--')
#ax[0,0].plot(dAC['bin']+1919,dAC['data']['PTF CN']['Coast']['Ctot L t0']['mu'],'ko',mfc='w',mec='k',ms=3)
ax[0,0].set(xticks=np.arange(1800,2200,20),ylabel='Tree biomass (tC/ha)',xlabel='Time, years',xlim=[1880,2150])
ax[0,0].legend(loc='lower right',facecolor=[1,1,1],frameon=False)
ax[0,0].yaxis.set_ticks_position('both'); ax[0,0].xaxis.set_ticks_position('both'); ax[0,0].tick_params(length=meta['Graphics']['gp']['tickl'])

## Growth
#plt.close('all'); fig,ax=plt.subplots(1,figsize=gu.cm2inch(18,14))
ind=np.where( (fp['PTF PSP']==1) & (fp['Ecozone BC L2']==meta['LUT']['GP']['Ecozone BC L2']['IDFdk']) )[0]
#ind=np.where( (fp['LS']=='FDC') )[0]
#ind=np.where( (fp['LS']=='FDC') & (fp['Ecozone BC L2']==meta['LUT']['GP']['Ecozone BC L2']['CWHdm']) )[0]
bw=10; bin=np.arange(10,200+bw,bw); N,mu,med,sig,se=gu.discres(fp['Age Mean t0'][ind],fp['Ctot L t0'][ind],bw,bin)
#bw=10; bin=np.arange(10,200+bw,bw); N,mu,med,sig,se=gu.discres(fp['Age Mean t0'][ind],fp['Ctot Net'][ind],bw,bin)
ax[0,0].plot(bin+1897,mu,'ko',ms=3,mfc='w')

ax[0,1].plot(tv,mos[pNam]['Scenarios'][iP]['Mean']['C_G_Net_Reg']['Ensemble Mean'][:,0,0,0],'k--',color=meta['Graphics']['gp']['cl2'],label='FCG25')
bw=10; bin=np.arange(10,200+bw,bw); N,mu,med,sig,se=gu.discres(fp['Age Mean t0'][ind],fp['Ctot Net'][ind],bw,bin)
ax[0,1].plot(bin+1897,mu,'ko',ms=3,mfc='w')

#%% Export tables for each scenario
tbs=udem.Export_Summary_Tables(meta,pNam,mos)

#%% Save to change tracker
udem.Record_In_ChangeTrackerDB(meta,pNam,mos,tbs,['Interior SR Class A','Interior NSR Class A','Interior NSR Class B'])

#%%
plt.close('all')
plt.plot(tv,mos[pNam]['Scenarios'][1]['Mean']['C_G_Net_Reg']['Ensemble Mean'][:,iPS,iSS,iYS],'b-')
plt.plot(tv,mos[pNam]['Scenarios'][2]['Mean']['C_G_Net_Reg']['Ensemble Mean'][:,iPS,iSS,iYS],'r--')

plt.close('all')
plt.plot(tv,3.667*np.cumsum(mos[pNam]['Scenarios'][2]['Mean']['C_G_Net_Reg']['Ensemble Mean'][:,iPS,iSS,iYS]-mos[pNam]['Scenarios'][1]['Mean']['C_G_Net_Reg']['Ensemble Mean'][:,iPS,iSS,iYS]),'b-')

#%% Graphic settings
t0=1950
t1=2150
cNam='Interior NSR Class A'

#%% Volume
plt.close('all')
td={'Year':np.array([2030,2050,2100,2145])}
udem.PlotVolumeMerchLive(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],
						 LegendLoc='upper left',FigSize=[16,6],TextDelta=td,FillDelta='On')

#%% Pools
plt.close('all')
td={'Year':np.array([2030,2050,2100,2145]),'Units':'Actual'}
udem.PlotPools(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='lower right',FigSize=[16,14],TextDelta=td)

#%% Fluxes
plt.close('all')
td={'Year':np.array([2100]),'Units':'Actual'}
udem.PlotFluxes(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='lower right',FigSize=[16,14],TextDelta=td)

#%% Fluxes Biomass
plt.close('all')
td={'Year':np.array([2100]),'Units':'Actual'}
udem.PlotFluxesBiomass(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='lower right',FigSize=[16,14],TextDelta=td)

#%% Delta GHG balance
plt.close('all')
udem.PlotDeltaGHGB(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],
				   LegendLoc='upper right',FigSize=[18,10])

#%% Schematic GHG balance
plt.close('all')
t0=meta[pNam]['Project']['Year Project']
#t1=2050
t1=meta[pNam]['Project']['Year Project']+100
ax=udem.PlotSchematicBalance(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

#%%
plt.close('all')
udem.PlotDeltaNEE(meta,mos,pNam,cNam=cNam,OperSpace='Mean',t0=t0,t1=t1,FigSize=[15,6])




