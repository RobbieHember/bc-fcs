#%% Import modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import fcgadgets.macgyver.util_general as gu
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun_preprocess as prep
import fcgadgets.cbrunner.cbrun_postprocess as post
import fcgadgets.cbrunner.cbrun as cbr
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.macgyver.util_demo as udem
import fcgadgets.macgyver.util_qa as uqa
import fcgadgets.gaia.gaia_util as gaia
import fcexplore.field_plots.Processing.fp_util as ufp
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Configure project
meta=u1ha.Init()
pNam='Demo_Harv_Clearcut'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=meta['Paths']['Projects']['Demos'] + '\\' + pNam
meta=cbu.ImportProjectConfig(meta,pNam)
meta['Graphics']['Print Figures']='On'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\Demo\Demo_Harv_Clearcut'

#%% Prepare inputs
prep.Write_BatchTIPSY_Input_File(meta,pNam)
prep.PrepareInventoryFromSpreadsheet(meta,pNam)
prep.BuildEventChronologyFromSpreadsheet(meta,pNam)
prep.PrepGrowthCurvesForCBR(meta,pNam)

#%% Run model
meta=cbr.MeepMeep(meta,pNam)

#%% Calculate summaries for future simulations
post.Calc_MOS_GHG(meta,pNam)
post.Calc_MOS_Econ(meta,pNam)
post.Calc_MOS_Area(meta,pNam)
post.Calc_MOS_MortByAgent(meta,pNam)

#%% Import data
pNam='Demo_Harv_Clearcut'
pth=meta['Paths']['Projects']['Demos'] + '\\' + pNam + '\\Inputs\\Metadata.pkl'
meta=gu.ipickle(pth)
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
mos=post.Import_MOS_ByScnAndStrata_GHGEcon(meta,pNam)
mos[pNam]['Delta']={}
mos[pNam]['Delta']['Interior']={'iB':0,'iP':1}
mos[pNam]['Delta']['Coast']={'iB':2,'iP':3}
mos=post.Import_MOS_ByScnComparisonAndStrata(meta,pNam,mos)
mos=gaia.Calc_RF_FAIR(meta,pNam,mos)
gaia.FAIR_BenchmarkPulse(meta,pNam,2020)
iPS=0; iSS=0; iYS=0; iOS=0;

#%% Comparison with CBM
uqa.QA_BenchmarkCBM_ClearcutCoast(meta,pNam,mos)

#%% Assess % of carbon remaining in HWP after 100 years
uqa.QA_Benchmark_HWP_ResidenceTime(meta)

#%%
plt.close('all')
plt.plot(tv,mos[pNam]['Scenarios'][iScn]['Mean']['C_InUse']['Ensemble Mean'][:,0,0,0],'g-')
plt.plot(tv,mos[pNam]['Scenarios'][iScn]['Mean']['C_WasteSystems']['Ensemble Mean'][:,0,0,0],'k-')

#%% Assess relative biomass apportionment
uqa.QA_AssessBiomassProportions(meta,mos)

#%% QA - conservation of mass analysis
iScn=3 # Coastal project
uqa.QA_ConservationOfMassTest_FromDemo(meta,pNam,mos,iScn)

#%% Radiative forcing summary
scnC='Coast'
frcL=['CO2','CH4','N2O','CO','Land use','Volcanic','Solar','Aerosol-cloud interactions','Aerosol-radiation interactions','Ozone','Stratospheric water vapour']
plt.close('all');
#plt.plot(tv,dFAIR['Delta'][scnC]['RF_Biochem'],'b-',lw=2)
for frc in frcL:
	plt.plot(tv,mos[pNam]['Delta'][scnC]['Data']['Mean']['RF_Chem_' + frc]['Ensemble Mean'],'-',lw=1,label=frc)
plt.legend()
plt.plot(tv,mos[pNam]['Delta'][scnC]['Data']['Mean']['RF_Chem_Total']['Ensemble Mean'],'b-',lw=2)
plt.plot(tv,mos[pNam]['Delta'][scnC]['Data']['Mean']['RF_Chem_CO2']['Ensemble Mean'],'b--',lw=2)
plt.plot(tv,mos[pNam]['Delta'][scnC]['Data']['Mean']['RF_Chem_N2O']['Ensemble Mean'],'m--',lw=2)
plt.plot(tv,mos[pNam]['Delta'][scnC]['Data']['Mean']['RF_Chem_CH4']['Ensemble Mean'],'r--',lw=2)
plt.plot(tv,mos[pNam]['Delta'][scnC]['Data']['Mean']['RF_Chem_CH4']['Ensemble Mean'],'r--',lw=2)

# Radiative forcing from Betts 2000
dE=post.GetMosDeltaVar(meta,pNam,mos,'Coast','E_NAB',iPS,iSS,iYS,iOS)['Mean']['Ensemble Mean'] # tCO2e/ha
dE=dE/3.66 # tC/ha/yr
dE=dE/1e9 # GtC/ha/yr
dE=dE/2.13 # ppm
CO2_Ref=400
RF=5.35*np.log(1+dE/CO2_Ref)*1e9 # nW m-2 ha-1
plt.plot(tv,np.cumsum(RF),'r--',lw=2)


MassOfAtmosphere=5.14*10**18 # kg
dE=dE*1000 # kgCO2/ha/yr
dE=dE/MassOfAtmosphere*1e6 # ppm
CO2_Ref=400
RF=5.35*np.log(1+dE/CO2_Ref)*1e9 # nW m-2 ha-1
plt.plot(tv,np.cumsum(RF),'r--',lw=2)
plt.plot(tv,RF,'r--',lw=2)



#v='RF_AlbedoSurfaceShortwave'
#y2=mos[pNam]['Delta'][scnC]['ByStrata']['Mean'][v]['Ensemble Mean'][:,iPS,iSS,iYS]
#plt.plot(tv,y2,'g--')
#plt.plot(tv,y1+y2,'k-.')


#%%
scnC='Coast'
plt.close('all')
for rf in meta['Modules']['FAIR']['Forcings']:
	plt.plot(tv,mos[pNam]['Delta'][scnC]['ByStrata']['Mean']['RF_Biochem_' + rf]['Ensemble Mean'][:,iPS,iSS,iYS],'-',lw=2,label=rf)
plt.legend()

#%% Export tables for each scenario
tbs=udem.Export_Summary_Tables(meta,pNam,mos)

#%% Save to change tracker
uqa.Record_In_ChangeTrackerDB(meta,pNam,mos,tbs,['Coast'])

#%% Harvest flow schematic
iScn=3
d=cbu.LoadSingleOutputFile(meta,'Demo_Harv_Clearcut',iScn,0,0)
iS=0
iH=np.where(d['C_Felled'][:,iS]>0)[0][0]
TimeHorizon=100
ufcs.Plot_QA_FateOfFelled(meta,d,iS,iH,TimeHorizon,'72')

#%% Export summary of economics (for work with Valentina)
vL=['V_ToMill_MerchTotal','V_ToMill_NonMerchTotal','Revenue Net','Revenue Gross','Cost Total']
df=udem.ExportTableScenariosAndDelta(meta,pNam,mos,
                                     cNam=['Interior'],
                                     NameTable='Summary Interior',
                                     OperTime='Sum',
                                     OperSpace='Mean',
                                     t0=meta[pNam]['Project']['Year Project'],
                                     t1=meta[pNam]['Project']['Year Project']+5,
                                     iPS=0,iSS=0,iYS=0,
                                     Units='Actual',
                                     Multiplier=1,
                                     Decimals=1,
									 Variables=vL,
                                     Save='On')

#%% Graphic settings
t0=1850
t1=2150
cNam='Coast'

#%% Volume
plt.close('all')
td={'Year':np.array([2030,2050,2100,2145])}
udem.PlotVolumeMerchLive(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],
						 LegendLoc='lower right',FigSize=[14,7],TextDelta=td,FillDelta='On',HarvestYears=[1914,2023])

#%% NEP
plt.close('all')
td={'Year':np.array([2030,2050,2100,2145])}
udem.PlotNEP(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline scenario','Action scenario'],LegendLoc='lower right',FigSize=[14,6],TextDelta=td,FillDelta='On')

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
udem.PlotDeltaGHGB(meta,mos,pNam,cNam=cNam,t0=t0,t1=t1,OperSpace='Mean',ScenarioLabels=['Baseline','Actual'],LegendLoc='upper right',FigSize=[16,10])

#%% Schematic GHG balance
plt.close('all')
t0=meta[pNam]['Project']['Year Project']
t1=meta[pNam]['Project']['Year Project']+100
ax=udem.PlotSchematicBalance(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

#%%

iB=0
iP=1
#y0=cbu.GetMosScnVar(meta,pNam,mos,iB,'E_NSB',0,0,0,0)['Mean']['Ensemble Mean']
y1=cbu.GetMosScnVar(meta,pNam,mos,iP,'E_NSB',0,0,0,0)['Mean']['Ensemble Mean']
plt.close('all')
#plt.plot(y0)
#plt.plot(np.cumsum(y1),'g--')
y2=cbu.GetMosScnVar(meta,pNam,mos,iP,'E_NAB',0,0,0,0)['Mean']['Ensemble Mean']
plt.plot(np.cumsum(y2)-np.cumsum(y1),'c.-')

#%%
#v='E_Domestic_ForestOperations'
#v='E_Substitution_Energy'
#v='E_Substitution_Material'
#v='E_Internat_ForestSector_HWP'
#v='E_Internat_Bioenergy'
v='E_Internat_ForestOperations'
y0=cbu.GetMosScnVar(meta,pNam,mos,iB,v,0,0,0,0)['Mean']['Ensemble Mean']
y1=cbu.GetMosScnVar(meta,pNam,mos,iP,v,0,0,0,0)['Mean']['Ensemble Mean']
plt.close('all')
plt.plot(y0)
plt.plot(y1,'g--')


#%% Plot NEE
plt.close('all')
udem.PlotDeltaNEE(meta,mos,pNam,cNam=cNam,OperSpace='Mean',t0=t0,t1=t1,FigSize=[15,6])

#%% Cashflow
udem.PlotCashflow(meta,pNam,mos,cNam=cNam,t0=t0,t1=t1)

#%% Plot all variables
#ufcs.AllVariableTimeSeries(meta,pNam,mos,tv,0,iT)

