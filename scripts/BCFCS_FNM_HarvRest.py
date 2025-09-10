'''
BC FOREST CARBON SUMMARY - NUTRIENT MANAGEMENT

Instructions:
-> Set Year Project and Year Start Cumulative to current year
-> Set start year of future disturbance to be current year + 1

Notes:
-> Database update is done in NOSE project script

'''
#%% Import Python modules
import numpy as np
import matplotlib.pyplot as plt
import time
import warnings
import fcgadgets.macgyver.util_general as gu
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.cbrunner.cbrun as cbr
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun_preprocess as prep
import fcgadgets.cbrunner.cbrun_postprocess as post
import fcgadgets.macgyver.util_nm as unm
import fcgadgets.macgyver.util_nose as unose
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.bc1ha.bc1ha_plot as p1ha
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Import BC1ha info
t0=time.time()
meta=u1ha.Init()
pNam='BCFCS_FNM_HarvRest'
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'D:\Modelling Projects\BCFCS_FNM_HarvRest'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\BCFCS\BCFCS_FNM_HarvRest\20250622'
meta['Graphics']['Print Figures']='On'

#%% Import project configuration
meta=cbu.ImportProjectConfig(meta,pNam)
meta[pNam]['YearCurrent']=2024
meta[pNam]['AIL CAP']=30000 # https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-investment-program/forest-investment-program-strategy-policy.pdf

#%% Index to baseline scenarios
meta[pNam]['Project']['Baseline Indices']=np.array([0])
meta[pNam]['Project']['Actual Indices']=np.array([1])

#%% Import input variables
meta,lsat,dmec=prep.Process1_ImportVariables(meta,pNam)

#%% prepare growth curves
gc,ugc,lsat,dmec=prep.Process2_PrepareGrowthCurves(meta,pNam,lsat,dmec)

#%% Run BatchTIPSY

# ************************* MANUAL OPERATION **********************************
#------------------------------------------------------------------------------
# Ensure BatchTIPSY.exe config (.BPS) file has up-to-date paths
# Run BatchTIPSY.exe
#------------------------------------------------------------------------------
# ************************* MANUAL OPERATION **********************************

#%% Define strata (for analyzing results)
meta=unm.DefineStrata(meta,pNam,dmec,lsat)

#%% prepare project inputs 3
meta,lsat,dmec=prep.Process3_PrepInputsByBatch(meta,pNam,lsat,dmec,gc,ugc)

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
	import fcgadgets.cbrunner.cbrun_preprocess as prep
	import fcgadgets.cbrunner.cbrun_postprocess as post
	import fcgadgets.bc1ha.bc1ha_utils as u1ha
	import fcgadgets.cbrunner.cbrun_util as cbu
	import fcgadgets.cbrunner.cbrun as cbr

	pNam='BCFCS_FNM_HarvRest'
	meta=gu.ipickle(r'D:\Modelling Projects\BCFCS_FNM_HarvRest\Inputs\Metadata.pkl')
	# cbu.DeleteAllOutputFiles(meta,pNam)
	meta=cbr.MeepMeep(meta,pNam)

#%% Calculate summaries for future simulations
post.Calc_MOS_GHG(meta,pNam)
post.Calc_MOS_Econ(meta,pNam)
post.Calc_MOS_Area(meta,pNam)
post.Calc_MOS_MortByAgent(meta,pNam)

#%% Import model results
pNam,meta,tv,mos,mosWF,dmec=unm.ImportModelResults()
cNam='Moderate Harvest'
t1=time.time()
print((t1-t0)/60)

#%% Import model results with harvest restrictions
pNam,meta,tv,mos,mosWF,mosPY,dmec=unm.ImportModelResults_HarvRest()
cNam='Moderate Harvest'

# Emissions stratified by biophysical process
unm.Plot_Emissions_ByBiophysProcess(meta,pNam,mos,cNam)

#%% QA plot map of operations (run bc1ha map with Province configuration)
p1ha.Plot_Map_FNM_ForTimeSpan(meta,roi,1971,meta[pNam]['YearCurrent'])
p1ha.Plot_Map_FNM_ForTimeSpan(meta,roi,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% QA Calculate MOS for every stand
mos_ByStand=cbu.Calc_MOS_ByStand(meta,mos,pNam,
								scnL=[0,1],
								time_horizon={'1971-2050':{'t0':1971,'t1':2050}, '1971-2100':{'t0':1971,'t1':2100}})

#  Save summary to spreadsheet (SummarySparseSample.xlsx) for troubleshooting, investigation, QA
iScn=1
unm.QA_PrintSummarySparseToSpreadsheet(meta,pNam,iScn,dmec,mos_ByStand,cNam)

# QA Plot individual stands
unm.QA_Plot_CarbonTimeSeriesByStand(meta,pNam,dmec)

#%% Plot time series of area treated by funding source
unm.Plot_AreaTreated_TimeSeries_ByFSC(meta,pNam)

#%% Plot frequency by funding source, BGC zone, species, and age at time of application
unm.Plot_AreaTreated_Frequency_ByFSC(meta,1971,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_Frequency_ByFSC(meta,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#d=unm.Plot_AreaTreated_FrequencyByBGC(meta,pNam,1971,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_Frequency_ByBGC(meta,pNam,2017,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_Frequency_ByBGC(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

unm.TabulateSpeciesComposition(meta,pNam,1971,meta[pNam]['YearCurrent'])
unm.TabulateSpeciesComposition(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_Frequency_BySpecies(meta,pNam,1971,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_Frequency_BySpecies(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

unm.Plot_AreaTreated_Frequency_ByAgeAtTimeOfApp(meta,pNam,1971,meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_Frequency_ByAgeAtTimeOfApp(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unm.Plot_AreaTreated_Frequency_BtVolMerchAtTimeOfApp(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
#unm.AreaTreated_FrequencyByLCC(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Area that has been harvested or burned
unm.AreaImpacted_ByDisturbance(meta,pNam)

#%% Area disturbaned and managed
iT=np.where( (tv>=1800) & (tv<=2150) )[0]
iScn=1
ufcs.Area_DisturbedAndManaged(meta,pNam,mos,1,iScn,iT,0,0,0,0,ncols=2,LegendLoc='upper right')

#%% Tabular summary of cumulative emissions by 2050 from implementation during current year (for Service Plan Annual Progress Report)
dE,dEpHa=unm.Tabulate_CurrentYear_ForServicePlan(meta,pNam,mos)
dEpHa
dE

#%% Emissions and yields by BGC zone
unm.Plot_EmissionsPerHectare_ForCurrentYear_ByBGC(meta,mos,pNam,cNam)
unm.Plot_YieldPerHectare_ForCurrentYear_ByBGC(meta,mos,pNam,cNam)

#%% Emissions stratified by biophysical process
unm.Plot_Emissions_ByBiophysProcess(meta,pNam,mos,cNam)

#%% Plot time series for current year (use for Service Plan)
#cNamL=['Low Harvest','High Harvest']
cNamL=['Moderate Harvest']
for cNam in cNamL:
	unm.Plot_Emissions_TS_AnnAndCumu_CurrentYear(meta,pNam,mos,cNam)
	unm.Plot_Emissions_TS_AnnualPerHectare_FromCurrentYear(meta,mos,pNam,cNam)
	unm.Plot_Emissions_TS_Annual_FromCurrentYear(meta,mos,pNam,cNam)
	unm.Plot_Emissions_TS_CumuPerHectare_FromCurrentYear(meta,mos,pNam,cNam)
	unm.Plot_Emissions_TS_AnnAndCumu_Completed(meta,pNam,mos,cNam)
	unm.Plot_Emissions_TS_AnnAndCumu_CompletedAndCAP(meta,pNam,mosWF,cNam)
	unm.Plot_Yield_TS_AnnAndCumu_CurrentYear(meta,pNam,mos,cNam)
	unm.Plot_Yield_TS_AnnAndCumu_Completed(meta,pNam,mos,cNam)
	unm.Plot_Yield_TS_AnnAndCumu_CompletedAndCAP(meta,pNam,mosWF,cNam)

#%% Cost and revenue assumptions
unm.Plot_RevenuePerM3_CurrentYear(meta,pNam,mos,cNam)

#%% Ensure net growth matches observations
unm.Plot_NetGrowthValidation(meta,mos,pNam)

#%% Plot delta pools
unm.Plot_PoolMeans_FromCurrentYear(meta,pNam,mos)

#%% Plot mitigation value
unm.Plot_MitigationValueUndiscounted(meta,mosWF,pNam)

#%% Plot cumulative GHG fluxes for each scenario comparison
#unm.Plot_FluxesCumulative_CompPlusCAP(meta,pNam,mosWF)

#%%
unm.Plot_Fluxes_TS_Cumulative_FromCurrentYear(meta,mos,pNam,cNam)

#%% Plot cumulative yield and economics for each scenario comparison
#unm.Plot_YieldCumulative(meta,pNam,mosWF)

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

#%%
iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']==str(meta[pNam]['YearCurrent']))[0][0]
plt.close('all')
iScn=0; y1=post.GetMosScnVar(meta,pNam,mos,iScn,'Area_Harvest',0,0,1,0)['Sum']['Ensemble Mean']
plt.plot(tv,y1,'b-')
iScn=1; y2=post.GetMosScnVar(meta,pNam,mos,iScn,'Area_Harvest',0,0,1,0)['Sum']['Ensemble Mean']
plt.plot(tv,y2,'g--')

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


#%% Experiments
dE=gu.ReadExcel(meta['Paths']['DB']['Nutrient Applications'] + '\\Forest Nutrient Addition Experiments DB.xlsx',sheet_name='Sheet1',skiprows=0)

#%% Net growth
elist=[]
elist.append({'Variable':'Exclusion Reason','Operator':'!=','Value':'nan'})
#elist.append({'Variable':'Territory','Operator':'!=','Value':'BC'})
elist.append({'Variable':'Duration (years)','Operator':'<','Value':7.5})
elist.append({'Variable':'Duration (years)','Operator':'>','Value':12.5})
elist.append({'Variable':'Thinned','Operator':'==','Value':'Yes'})
elist.append({'Variable':'N Num Applications','Operator':'>','Value':1})
elist.append({'Variable':'N Dose Per Application (kgN/ha)','Operator':'<','Value':150})
elist.append({'Variable':'N Dose Per Application (kgN/ha)','Operator':'>','Value':250})
elist.append({'Variable':'Stemwood Biomass Growth Net Units Combined','Operator':'!=','Value':'MgC/ha/yr'})
elist.append({'Variable':'Stemwood Biomass Growth Net Difference Relative Combined (%)','Operator':'<','Value':-100})
elist.append({'Variable':'Stemwood Biomass Growth Net Difference Relative Combined (%)','Operator':'>','Value':2000})
elist.append({'Variable':'Stemwood Biomass Growth Net Difference Relative Combined (%)','Operator':'isnan','Value':[]})
ikp,ExcActual,ExcActualUnique,ExcPercent,RemainA,RemainP=gu.IndexAndTrackExclusions(dE,elist)
RemainA

dEI={}
for v in dE.keys():
	dEI[v]=dE[v][ikp]

vL=['Duration (years)','Stemwood Biomass Growth Net Difference Actual Combined','Stemwood Biomass Growth Net Difference Relative Combined (%)']
dES={}
for v in dEI.keys():
	try:
		dES[v]={}
		dES[v]['N']=ikp.size
		dES[v]['Mean']=np.nanmean(dEI[v])
		dES[v]['Median']=np.nanmedian(dEI[v])
		dES[v]['Weighted average']=np.nansum(dEI[v]*dEI['Num Sites'])/np.sum(dEI['Num Sites'])
		dES[v]['S.E.']=np.nanstd(dEI[v])/np.sqrt(ikp.size)
	except:
		pass

#dES['Stemwood Biomass Growth Net Difference Actual Combined']
print(dES['Stemwood Biomass Growth Net Difference Relative Combined (%)'])

#%% Gross growth
elist=[]
elist.append({'Variable':'Exclusion Reason','Operator':'!=','Value':'nan'})
#elist.append({'Variable':'Territory','Operator':'!=','Value':'BC'})
#elist.append({'Variable':'Duration (years)','Operator':'<','Value':7.5})
#elist.append({'Variable':'Duration (years)','Operator':'>','Value':12.5})
elist.append({'Variable':'Thinned','Operator':'==','Value':'Yes'})
#elist.append({'Variable':'N Num Applications','Operator':'>','Value':1})
#elist.append({'Variable':'N Dose Per Application (kgN/ha)','Operator':'<','Value':150})
#elist.append({'Variable':'N Dose Per Application (kgN/ha)','Operator':'>','Value':250})
elist.append({'Variable':'Stemwood Biomass Growth Gross Units Combined','Operator':'!=','Value':'MgC/ha/yr'})
elist.append({'Variable':'Stemwood Biomass Growth Gross Difference Relative Combined (%)','Operator':'<','Value':-100})
elist.append({'Variable':'Stemwood Biomass Growth Gross Difference Relative Combined (%)','Operator':'>','Value':2000})
elist.append({'Variable':'Stemwood Biomass Growth Gross Difference Relative Combined (%)','Operator':'isnan','Value':[]})
ikp,ExcActual,ExcActualUnique,ExcPercent,RemainA,RemainP=gu.IndexAndTrackExclusions(dE,elist)
RemainA

dEI={}
for v in dE.keys():
	dEI[v]=dE[v][ikp]

vL=['Duration (years)','Stemwood Biomass Growth Net Difference Actual Combined','Stemwood Biomass Growth Net Difference Relative Combined (%)']
dES={}
for v in dEI.keys():
	try:
		dES[v]={}
		dES[v]['N']=ikp.size
		dES[v]['Mean']=np.nanmean(dEI[v])
		dES[v]['Median']=np.nanmedian(dEI[v])
		dES[v]['Weighted average']=np.nansum(dEI[v]*dEI['Num Sites'])/np.sum(dEI['Num Sites'])
		dES[v]['S.E.']=np.nanstd(dEI[v])/np.sqrt(ikp.size)
	except:
		pass

#dES['Stemwood Biomass Growth Gross Difference Actual Combined']
print(dES['Stemwood Biomass Growth Gross Difference Relative Combined (%)'])

#%% Mortality
elist=[]
elist.append({'Variable':'Exclusion Reason','Operator':'!=','Value':'nan'})
#elist.append({'Variable':'Territory','Operator':'!=','Value':'BC'})
#elist.append({'Variable':'Duration (years)','Operator':'<','Value':7.5})
#elist.append({'Variable':'Duration (years)','Operator':'>','Value':12.5})
elist.append({'Variable':'Thinned','Operator':'==','Value':'Yes'})
#elist.append({'Variable':'N Num Applications','Operator':'>','Value':1})
#elist.append({'Variable':'N Dose Per Application (kgN/ha)','Operator':'<','Value':150})
#elist.append({'Variable':'N Dose Per Application (kgN/ha)','Operator':'>','Value':250})
elist.append({'Variable':'Stemwood Biomass Mortality Units Combined','Operator':'!=','Value':'MgC/ha/yr'})
elist.append({'Variable':'Stemwood Biomass Mortality Difference Relative Combined (%)','Operator':'<','Value':-100})
elist.append({'Variable':'Stemwood Biomass Mortality Difference Relative Combined (%)','Operator':'>','Value':2000})
elist.append({'Variable':'Stemwood Biomass Mortality Difference Relative Combined (%)','Operator':'isnan','Value':[]})
ikp,ExcActual,ExcActualUnique,ExcPercent,RemainA,RemainP=gu.IndexAndTrackExclusions(dE,elist)
RemainA

dEI={}
for v in dE.keys():
	dEI[v]=dE[v][ikp]

vL=['Duration (years)','Stemwood Biomass Growth Net Difference Actual Combined','Stemwood Biomass Growth Net Difference Relative Combined (%)']
dES={}
for v in dEI.keys():
	try:
		dES[v]={}
		dES[v]['N']=ikp.size
		dES[v]['Mean']=np.nanmean(dEI[v])
		dES[v]['Median']=np.nanmedian(dEI[v])
		dES[v]['Weighted average']=np.nansum(dEI[v]*dEI['Num Sites'])/np.sum(dEI['Num Sites'])
		dES[v]['S.E.']=np.nanstd(dEI[v])/np.sqrt(ikp.size)
	except:
		pass

print(dES['Stemwood Biomass Mortality Difference Relative Combined (%)'])
