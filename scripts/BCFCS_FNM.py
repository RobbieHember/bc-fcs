'''
BC FOREST CARBON SUMMARY - NUTRIENT MANAGEMENT COMPLETED
Instructions:
- Set Year Project and Year Start Cumulative to current year
'''
#%% Import Python modules
import numpy as np
import matplotlib.pyplot as plt
import time
import warnings
import fcgadgets.macgyver.util_general as gu
import fcgadgets.macgyver.util_inventory as uinv
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.macgyver.util_nm as unm
import fcgadgets.macgyver.util_nose as unose
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun as cbr
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Import BC1ha info
t0=time.time()
meta=u1ha.Init()
pNam='BCFCS_NMC'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'C:\Data\BCFCS\BCFCS_NMC'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\BCFCS\BCFCS_NM\Completed\2024-09-01'
meta['Graphics']['Print Figures']='On'

#%% Import project configuration
meta=cbu.ImportProjectConfig(meta,pNam)
meta[pNam]['YearCurrent']=2023
meta[pNam]['AIL CAP']=30000 # https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-investment-program/forest-investment-program-strategy-policy.pdf

#%% Index to baseline scenarios
meta[pNam]['Project']['Baseline Indices']=np.array([0,2])
meta[pNam]['Project']['Actual Indices']=np.array([1,3])

#%% Import input variables
meta,lsat,dmec=uinv.Process1_ImportVariables(meta,pNam)

#%% Prepare growth curves
gc,ugc,lsat,dmec=uinv.Process2_PrepareGrowthCurves(meta,pNam,lsat,dmec)

#%% Run BatchTIPSY

# ************************* MANUAL OPERATION **********************************
#------------------------------------------------------------------------------
# Ensure BatchTIPSY.exe config (.BPS) file has up-to-date paths
# Run BatchTIPSY.exe
#------------------------------------------------------------------------------
# ************************* MANUAL OPERATION **********************************

#%% Define strata (for analyzing results)
meta=unm.DefineStrata(meta,pNam,dmec,lsat,status_pt='Off',status_t='On',status_s='On')

#%% Prepare project inputs 3
meta,lsat,dmec=uinv.Process3_PrepInputsByBatch(meta,pNam,lsat,dmec,gc,ugc)

#%% Run simulation
meta=cbr.MeepMeep(meta,pNam)
meta[pNam]['Project']['Run Time Summary']

#%% If running multiple instances:
flg=0
if flg==1:
	import numpy as np
	import matplotlib.pyplot as plt
	import time
	import fcgadgets.macgyver.util_general as gu
	import fcgadgets.macgyver.util_inventory as uinv
	import fcgadgets.bc1ha.bc1ha_utils as u1ha
	import fcgadgets.cbrunner.cbrun_util as cbu
	import fcgadgets.cbrunner.cbrun as cbr

	pNam='BCFCS_NMC'
	meta=gu.ipickle(r'C:\Data\BCFCS\BCFCS_NMC\Inputs\Metadata.pkl')
	# cbu.DeleteAllOutputFiles(meta,pNam)
	meta=cbr.MeepMeep(meta,pNam)

#%% Calculate summaries for future simulations
cbu.Calc_MOS_GHG(meta,pNam)
cbu.Calc_MOS_Econ(meta,pNam)
cbu.Calc_MOS_Area(meta,pNam)
cbu.Calc_MOS_MortByAgent(meta,pNam)

#%% Import model results
pNam,meta,tv,mos,mosWF,dmec=unm.ImportModelResults()
t1=time.time()
print((t1-t0)/60)

#%% QA Calculate mean values for every stand
E_sum,E_mu=unm.SummarizeBenefitForEachStand(meta,pNam,mos)

#%% QA Save summary to spreadsheet (sparse sample) for troubleshooting, investigation, QA
iScn=1
unm.QA_PrintSummarySparseToSpreadsheet(meta,pNam,iScn,dmec,E_sum)

#%% QA Plot individual stands
unm.QA_Plot_CarbonTimeSeriesByStand(meta,pNam,dmec)

#%% Plot time series of area treated by funding source
unm.Plot_AreaTreated_TimeSeriesByFSC(meta,pNam)

#%% Plot frequency of treatment by funding source
unm.Plot_AreaTreated_FrequencyByFSC(meta,1960,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_FrequencyByFSC(meta,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Plot frequency by leading species (takes a few minutes)
unm.TabulateSpeciesComposition(meta,pNam,1960,meta[pNam]['YearCurrent'])
unm.Plot_TreatmentFrequency_BySpecies(meta,pNam,1960,meta[pNam]['YearCurrent'])
unm.TabulateSpeciesComposition(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unm.Plot_TreatmentFrequency_BySpecies(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Age at time of application for specific BGC zone and time period
unm.AgeAtTimeOfApplication(meta,pNam,2023,2023)

#%% Plot frequency of treatment by BGC zone
d=unm.Plot_AreaTreated_FrequencyByBGC(meta,pNam,1960,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_FrequencyByBGC(meta,pNam,2017,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_FrequencyByBGC(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Plot frequency by land cover class
unm.AreaTreated_FrequencyByLCC(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Area that has been harvested or burned
unm.AreaImpactedByDisturbance(meta,pNam,t0,t1)

#%% Area disturbaned and managed
iT=np.where( (tv>=1800) & (tv<=2150) )[0]
iScn=3
ufcs.Area_DisturbedAndManaged(meta,pNam,mos,1,iScn,iT,0,0,0)

#%% Tabular summary of cumulative emissions by 2050 from implementation during current year (for Service Plan Annual Progress Report)
d=unm.SummarizeServicePlan(meta,pNam,mos)

d['Total']['Low Harvest']
d['PerHa']['High Harvest']

#%%
unm.Plot_PerHectareEmissionsByBGCZone(meta,pNam,d)

#%% Plot time series for current year (use for Service Plan)
#unm.Plot_EmissionsAnnual_TimeSeriesFromCurrentYear(meta,mos,pNam)
#unm.Plot_EmissionsCumu_TimeSeriesFromCurrentYear(meta,mos,pNam)
cNam='High Harvest'
unm.Plot_EmissionsAnnAndCumu_TimeSeriesCurrentYear(meta,mos,pNam,cNam)

#%%
unm.Plot_EmissionsAnnualPerHectare_TimeSeriesFromCurrentYear(meta,mos,pNam)
unm.Plot_EmissionsCumuPerHectare_TimeSeriesFromCurrentYear(meta,mos,pNam)

#%% Plot time series for all completed operations
cNam='High Harvest'
cNam='Low Harvest'
unm.Plot_EmissionsAnnAndCumu_TimeSeriesCompleted(meta,pNam,mos,cNam)
unm.Plot_EmissionsAnnAndCumu_TimeSeries_CompletedAndCAP(meta,pNam,mosWF,cNam)

#%%
cNam='High Harvest'
cNam='Low Harvest'
unm.Plot_YieldAnnAndCumu_TimeSeriesCompleted(meta,pNam,mos,cNam)
unm.Plot_YieldAnnAndCumu_TimeSeriesCompletedAndCAP(meta,pNam,mosWF,cNam)

#%%

cNam='Low Harvest'
iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']=='All')[0][0]
y0=mos[pNam]['Delta'][cNam]['ByStrata']['Sum']['E_AGHGB_WOSub_cumu']['Ensemble Mean'][:,iPS,iSS,iYS]/1e6
y1=np.cumsum(mos[pNam]['Delta'][cNam]['ByStrata']['Sum']['E_AGHGB_WOSub']['Ensemble Mean'][:,0,0,iYS]/1e6)
plt.plot(tv,y0,'b-')
plt.plot(tv,y1,'g--')

#%%
#unm.PlotSummaryCombined(meta,mos,pNamC,pNamF,cNam)

#%% Plot mitigation value
iPS=0; iSS=0; iYS=0
unm.Plot_MitigationValueUndiscounted(meta,mosWF,pNam,iPS,iSS,iYS)

#%%
unm.SummarizeFluxesCumulative(meta,pNam,mosWF)

#%%
unm.SummarizeYieldCumulative(meta,pNam,mosWF)






#%%
iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']=='2023')[0][0]
plt.close('all')
#plt.plot(tv,mos[pNam]['Delta']['NM1']['ByStrata']['Mean']['E_AGHGB_WHSub']['Ensemble Mean'][:,iPS,iSS,iYS],'-b.')
plt.plot(tv,mos[pNam]['Delta']['NM1']['ByStrata']['Mean']['C_Biomass']['Ensemble Mean'][:,iPS,iSS,iYS],'-b.')


#%%
#ufcs.RunOutputGraphics(meta,pNam,lsat,mos,dR,iPS,iSS,iYS,iT,gpt,dH_ByBGCZ)

#%%
#ufcs.CarbonFluxTimeSeries(meta,pNam,mos,iT,1,iPS,iSS,iYS)

#%%
#iT=np.where( (tv>=1800) & (tv<=2150) )[0]
#ufcs.ScenarioComp_GHGBalanceAnnualPlusCumu(meta,pNam,mos,cNam,iT,0,0,0)

#%%
#ufcs.ScenarioComp_GHGBalanceAnnual(meta,pNam,mos,cNam,iT,iPS,iSS,iYS)

#%%
#ufcs.ScenarioComp_ForcingBarChart(meta,pNam,mos,tv,c,iPS,iSS,iYS)

#v='E_AGHGB_WOSub_cumu'
#v='A'
v='V_ToMillTotalMerch'
plt.close('all');
cNam='Low Harvest';plt.plot(tv,np.cumsum(mos[pNam]['Delta'][cNam]['ByStrata']['Sum'][v]['Ensemble Mean'][:,0,0,0]/meta[pNam]['Project']['Multi']),'b-')
cNam='High Harvest';plt.plot(tv,np.cumsum(mos[pNam]['Delta'][cNam]['ByStrata']['Sum'][v]['Ensemble Mean'][:,0,0,0]/meta[pNam]['Project']['Multi']),'g--')

#%%
v='Revenue Net'
plt.close('all');
cNam='Low Harvest';plt.plot(tv,np.cumsum(mos[pNam]['Delta'][cNam]['ByStrata']['Sum'][v]['Ensemble Mean'][:,0,0,0]/meta[pNam]['Project']['Multi']),'b-')
cNam='High Harvest';plt.plot(tv,np.cumsum(mos[pNam]['Delta'][cNam]['ByStrata']['Sum'][v]['Ensemble Mean'][:,0,0,0]/meta[pNam]['Project']['Multi']),'g--')


v='Revenue Net'
plt.close('all');
plt.plot(tv,np.cumsum(mos[pNam]['Delta'][cNam]['ByStrata']['Sum'][v]['Ensemble Mean'][:,0,0,0]/meta[pNam]['Project']['Multi']),'b-')



#%%
plt.close('all')
plt.plot(tv,mos[pNam]['Scenarios'][0]['Sum']['Area_Harvest']['Ensemble Mean'][:,0,0,0],'b-')
plt.plot(tv,mos[pNam]['Scenarios'][1]['Sum']['Area_Harvest']['Ensemble Mean'][:,0,0,0],'g--')



#%% QA Check integrity of biomass pools

bfv=0.41*0.5*mos[pNam]['Scenarios'][iScnA]['Mean']['V_MerchTotal']['Ensemble Mean'][:,iPS,iSS,iYS]
bsw=mos[pNam]['Scenarios'][iScnA]['Mean']['C_Stemwood_Tot']['Ensemble Mean'][:,iPS,iSS,iYS]
br=mos[pNam]['Scenarios'][iScnA]['Mean']['C_Root_Tot']['Ensemble Mean'][:,iPS,iSS,iYS]
bt=mos[pNam]['Scenarios'][iScnA]['Mean']['C_Biomass_Tot']['Ensemble Mean'][:,iPS,iSS,iYS]
print(np.nanmean(bfv))
print(np.nanmean(bsw))
print(np.nanmean(br))
print(np.nanmean(bt))
print(np.nanmean(bsw/bt))