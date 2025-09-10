'''
BC FOREST CARBON SUMMARY - NON-OBLIGATION STAND ESTABLISHMENT COMPLETED

Instructions:

	Update Year Project to reflect current year
'''

#%% Import Python modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import warnings
import fcgadgets.macgyver.util_general as gu
import fcgadgets.macgyver.util_gis as gis
import fcgadgets.cbrunner.cbrun_preprocess as prep
import fcgadgets.cbrunner.cbrun_postprocess as post
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun as cbr
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.macgyver.util_fcs_qa as uqa
import fcgadgets.macgyver.util_nose as unose
import fcgadgets.macgyver.util_nm as unm
import fcgadgets.bc1ha.bc1ha_plot as p1ha
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Import BC1ha info
pNam='BCFCS_NOSE'
meta=u1ha.Init()
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'D:\Modelling Projects\BCFCS_NOSE' #meta['Paths'][pNam]['Data']=r'C:\Data\BCFCS\BCFCS_NOSE'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\BCFCS\BCFCS_NOSE\2025-05-15'
meta['Graphics']['Print Figures']='On'

#%% Import project configuration
meta=cbu.ImportProjectConfig(meta,pNam)
meta[pNam]['YearCurrent']=2024

#%% Index to baseline scenarios
meta[pNam]['Project']['Baseline Indices']=np.array([0])
meta[pNam]['Project']['Actual Indices']=np.array([1])

#%% Import input variables.
meta,lsat,dmec=prep.Process1_ImportVariables(meta,pNam)

#%% Prepare growth curves
gc,ugc,lsat,dmec=prep.Process2_PrepareGrowthCurves(meta,pNam,lsat,dmec)

#%% Run BatchTIPSY

# ************************* MANUAL OPERATION **********************************
#------------------------------------------------------------------------------
# Ensure BatchTIPSY.exe config (.BPS) file has up-to-date paths
# Run BatchTIPSY.exe
#------------------------------------------------------------------------------
# ************************* MANUAL OPERATION **********************************

#%% Define strata (for analyzing results)
meta=unose.DefineStrata(meta,pNam,dmec,lsat)
#idx=gu.IndicesFromUniqueArrayValues(meta[pNam]['Project']['Strata']['Other']['ID'])

#%% Prepare project inputs 3
meta,lsat,dmec=prep.Process3_PrepInputsByBatch(meta,pNam,lsat,dmec,gc,ugc)

#%% Run simulation
t0=time.time()
meta=cbr.MeepMeep(meta,pNam)
print((time.time()-t0)/60)

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

	pNam='BCFCS_NOSE'
	meta=gu.ipickle(r'D:\Modelling Projects\BCFCS_NOSE\Inputs\Metadata.pkl')
	# cbu.DeleteAllOutputFiles(meta,pNam)
	meta=cbr.MeepMeep(meta,pNam)

#%% Calculate model output statistics
cbu.Calc_MOS_GHG(meta,pNam)
cbu.Calc_MOS_Econ(meta,pNam)
cbu.Calc_MOS_Area(meta,pNam)
cbu.Calc_MOS_MortByAgent(meta,pNam)

#%% Import model results (takes 26 min with 100 ensembles)
t0=time.time()
pNam,meta,tv,mos,dmec=unose.ImportModelResults()
cNam='NOSE'
print((time.time()-t0)/60)

#%%
v='E_NSB'
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
tv0=np.arange(2018,2025,1)

fscL=['FIP','FCE','FCM','FES','FTM','FTL']
cNam='NOSE'

dE={'Total':{},'Efficacy':{},'tv':tv0}
for iPT in range(meta[pNam]['Project']['Strata']['Project Type']['Unique CD'].size):
	pt=meta[pNam]['Project']['Strata']['Project Type']['Unique CD'][iPT]
	dE['Total'][pt]=np.zeros(tv0.size)
	dE['Efficacy'][pt]=np.zeros(tv0.size)
	for iY in range(tv0.size):
		ind=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']==str(tv0[iY]))[0]
		yr=meta[pNam]['Project']['Strata']['Year']['Unique CD'][ind]

		iT=np.where( (tv>=int(yr)-10) & (tv<=2050) )[0]

		iPS=np.where(meta[pNam]['Project']['Strata']['Project Type']['Unique CD']==pt)[0][0]
		iSS=np.where(meta[pNam]['Project']['Strata']['Spatial']['Unique CD']=='All')[0][0]
		iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']==yr)[0][0]

		for fsc in fscL:
			iOS=np.where(meta[pNam]['Project']['Strata']['Other']['Unique CD']==fsc)[0][0]

			# Total
			y=np.nan_to_num(np.sum(cbu.GetMosDeltaVar(meta,pNam,mos,cNam,v,iPS,iSS,iYS,iOS)['Sum']['Ensemble Mean'][iT]))/meta[pNam]['Project']['Multi']
			dE['Total'][pt][iY]=dE['Total'][pt][iY]+y
	
			# Per-hectare
			y=np.nan_to_num(np.sum(cbu.GetMosDeltaVar(meta,pNam,mos,cNam,v,iPS,iSS,iYS,iOS)['Mean']['Ensemble Mean'][iT]))
			dE['Efficacy'][pt][iY]=dE['Efficacy'][pt][iY]+y
		dE['Efficacy'][pt][iY]=dE['Efficacy'][pt][iY]/len(fscL)

#%% Import area of treatment
dA=gu.ipickle(meta['Paths']['bc1ha'] + '\\RSLT_ACTIVITY_TREATMENT_SVW\\ASET_SummaryByTimeAndFSC.pkl')
dA['Data']['All']={}
for pt in dA['Data']['FIP'].keys():
	dA['Data']['All'][pt]=np.zeros(dA['Data']['FIP'][pt].size)
	for fsc in dA['Data'].keys():
		if np.isin(fsc,fscL)==True:
			dA['Data']['All'][pt]=dA['Data']['All'][pt]+dA['Data'][fsc][pt]

#%%

#pt='Knockdown and Planting'
pt='Underplanting'
for pt in dE['Total'].keys():
	if pt=='All': continue
	cl=meta['Graphics']['Colours']['rgb']['Green Neon']
	plt.close('all'); fig,ax=plt.subplots(3,1,figsize=gu.cm2inch(10,12));
	
	ax[0].bar(dA['tv'],dA['Data']['All'][pt]/1e3,0.85,facecolor=cl)
	ax[0].set(ylabel='Area (Kha yr$^{-1}$)',xticks=dE['tv'],xlim=[dE['tv'][0]-0.5,dE['tv'][-1]+0.5])
	ax[0].yaxis.set_ticks_position('both'); ax[0].xaxis.set_ticks_position('both'); ax[0].tick_params(length=meta['Graphics']['gp']['tickl'])
	
	ax[1].plot([2017,2030],[0,0],'k-')
	#ax[1].bar(dE['tv'],dE['Efficacy'][pt],0.85,facecolor=cl)
	ax[1].bar(dE['tv'],(dE['Total'][pt]*1e6)/dA['Data']['All'][pt],0.85,facecolor=cl)
	#ax[1].plot(dE['tv'],(dE['Total'][pt]*1e6)/dA['Data']['All'][pt],'-ko')
	ax[1].set(ylabel='Efficacy (tCO$_2$e ha$^{-1}$)',xticks=dE['tv'],xlim=[dE['tv'][0]-0.5,dE['tv'][-1]+0.5])
	ax[1].yaxis.set_ticks_position('both'); ax[1].xaxis.set_ticks_position('both'); ax[1].tick_params(length=meta['Graphics']['gp']['tickl'])
	
	ax[2].plot([2017,2030],[0,0],'k-')
	ax[2].bar(dE['tv'],dE['Total'][pt],0.85,facecolor=cl)
	#ax[2].plot(dE['tv'],(dA['Data']['All'][pt]*dE['Efficacy'][pt])/1e6,'-ko')
	ax[2].set(ylabel='Emissions (MtCO$_2$e ha$^{-1}$)',xticks=dE['tv'],xlim=[dE['tv'][0]-0.5,dE['tv'][-1]+0.5])
	ax[2].yaxis.set_ticks_position('both'); ax[2].xaxis.set_ticks_position('both'); ax[2].tick_params(length=meta['Graphics']['gp']['tickl'])
	
	gu.axletters(ax,plt,0.035,0.85,FontColor=meta['Graphics']['gp']['cla'],LetterStyle=meta['Graphics']['Modelling']['AxesLetterStyle'],FontWeight=meta['Graphics']['Modelling']['AxesFontWeight'])
	plt.tight_layout()
	if meta['Graphics']['Print Figures']=='On':
		gu.PrintFig(meta['Graphics']['Print Figure Path'] + '\\HistoricalSummary_' + pt,'png',900)

#%% Project future implementation
meta[pNam]['AIL CAP']=45000000/1850 # https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-investment-program/forest-investment-program-strategy-policy.pdf

fracPT={'Salvage and Planting Post Beetle':0.2,
	   'Knockdown and Planting':0.0,
	   'Road Rehabilitation':0.0,
	   'Underplanting':0.8,
	   'Replanting':0.0,
	   'Fill Planting':0.0,
	   'Ecosystem Restoration':0}

# Full projection
mosWF=unose.ProjectFuture(meta,pNam,mos,'Full',fracPT)

# SP Projection year
mosPY=unose.ProjectFuture(meta,pNam,mos,'SP Projection',fracPT)

#%% Save for Jupyter
# gu.opickle(r'C:\Data\BCFCS\BCFCS_NOSE\Outputs\MOS.pkl',mos)

#%% Sensitivity to overstory removal fraction

#%% Fraction of overstory removal
dSor=unose.Calculate_FractionOverstoryRemoval(meta,pNam,mos)
unose.SensitivityToOverstoryRemovalFrac(meta,pNam,mos,dSor)

#%% Validation against observed net growth
unose.QA_Plot_Validation_NetGrowth_ByBGC(meta,mos,pNam)
unose.QA_Plot_Validation_NetGrowth_ByProjectType(meta,mos,pNam)

#%% Plot map of operations (run bc1ha map with Province configuration first)
p1ha.Plot_Map_NOSE_ForTimeSpan(meta,roi,1971,meta[pNam]['YearCurrent'])
p1ha.Plot_Map_NOSE_ForTimeSpan(meta,roi,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Quality assurance / troubleshooting resources

# Calculate MOS for every stand (to support QA and troubleshooting) (takes a few minutes)
mos_ByStand=cbu.Calc_MOS_ByStand(meta,mos,pNam,
								scnL=[0,1],
								time_horizon={'1971-2050':{'t0':1971,'t1':2050},'1971-2100':{'t0':1971,'t1':2100}})

# Save summary sample of stand info to spreadsheet (for troubleshooting) (takes several minutes)
unose.QA_Print_SummarySparseToSpreadsheet(meta,pNam,meta[pNam]['Project']['Actual Indices'][0],dmec,mos_ByStand,cNam)

# Plot specific set of of stands (for troubleshooting)
unose.QA_Plot_Carbon_TS_ByStandSelect(meta,pNam,dmec,Index=np.array([2740]))

# Plot a sample of stands (for troubleshooting)
unose.QA_Plot_Carbon_TS_ByStand(meta,pNam,dmec)
unose.QA_Plot_Carbon_TS_ByStand(meta,pNam,dmec,pt=['Salvage and Planting Post Beetle'])

#%% Summarize area treated
unose.Plot_AreaTreated_TS_ByASET(meta,pNam,'NOSE',FigSize=[22,10])
unose.Plot_AreaTreated_TS_ByASET(meta,pNam,'Licensees',FigSize=[22,10])
unose.Plot_AreaTreated_TS_ByASET(meta,pNam,'All',FigSize=[22,10])
unose.Plot_AreaTreated_Frequency_ByASET(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

unose.Plot_AreaTreated_Frequency_ByFSC(meta,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unose.Plot_AreaTreated_Frequency_ByFSC(meta,1971,meta[pNam]['YearCurrent']+1)
unose.Plot_AreaTreated_TS_Ann_ByFSC(meta,pNam)

unose.Plot_AreaTreated_Frequency_ByBGC(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unose.Plot_AreaTreated_Frequency_ByBGC(meta,pNam,1971,meta[pNam]['YearCurrent'])
unose.Plot_AreaTreated_Frequency_ByBGC(meta,pNam,2017,meta[pNam]['YearCurrent'])

unose.Tabulate_SpeciesComposition(meta,pNam,1971,meta[pNam]['YearCurrent'])
unose.Tabulate_SpeciesComposition(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unose.Plot_AreaTreated_Frequency_BySpecies(meta,pNam,1971,meta[pNam]['YearCurrent'])
unose.Plot_AreaTreated_Frequency_BySpecies(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
#d=unose.Tabulate_UnderplantingByBurnSeverityClass(meta)

#%% Tabular summary of cumulative emissions by 2050 from implementation during current year (for Service Plan Annual Progress Report)
osL=['FIP']
#osL=['FED']
#osL=['FTM']
#osL=['FIP','FCE','FCM','FTM','FED']
#osL=['All']
dE,dEpHa=unose.Tabulate_CurrentYear_ForServicePlan(meta,pNam,mos,cNam,osL)
dE
dEpHa
print(dE['Salvage and Planting Post Beetle']+dE['Knockdown and Planting']+dE['Underplanting']+dE['Straight-to-planting Post Beetles']+dE['Fill Planting']+dE['Replanting'])

#%% Emissions by funding source
unose.Plot_Emissions_Cumu2050_ByFSC(meta,mos,pNam,cNam)
unose.Plot_EmissionsPerHa_Cumu2050_ByFSC(meta,mos,pNam,cNam)

#%% Per-hectare emissions by BGC zone
#fsc='FIP'
fsc='All'
unose.Plot_EmissionsPerHectare_CurrentYear_ByBGC(meta,mos,pNam,cNam,fsc)

#%% Emissions for current year (use for Service Plan)
fsc='FIP'
unose.Plot_EmissionsPerHectare_TS_Annual_FromCurrentYear_ByASET(meta,mos,pNam,cNam)
unose.Plot_EmissionsPerHectare_TS_Cumu_FromCurrentYear_ByASET(meta,mos,pNam,cNam,fsc)
unose.Plot_Emissions_TS_Annual_FromCurrentYear_ByASET(meta,mos,pNam,cNam)
unose.Plot_Emissions_TS_Cumu_FromCurrentYear_ByASET(meta,mos,pNam,cNam)
unose.Plot_Emissions_TS_AnnAndCumu_CurrentYear(meta,mos,pNam,cNam,fsc)

#%% Emissions for projection year (used for the Service Plan)
unose.Plot_Emissions_TS_AnnAndCumu_ProjectionYear(meta,mosPY,pNam,cNam)

#%% Emissions for completed
unose.Plot_Emissions_TS_Ann_Completed_ByASET(meta,mos,pNam,cNam)
unose.Plot_Emissions_TS_Cumu_Completed_ByASET(meta,mos,pNam,cNam)
unose.Plot_Emissions_TS_AnnAndCumu_Completed(meta,mos,pNam,cNam)

#%% Emissions for completed+CAP
unose.Plot_Emissions_TS_AnnAndCumu_CompletedAndCAP(meta,mosWF,pNam,cNam)
#unose.Plot_Emissions_TS_AnnAndCumu_CompletedAndCAP_WithScenarios(meta,mosWF,pNam,cNam)

#%% Carbon fluxes
fsc='FIP'
unose.Plot_Fluxes_TS_Annual_FromCurrentYear_ByASET(meta,mos,pNam,cNam,fsc)
unose.Plot_Fluxes_TS_Cumulative_FromCurrentYear_ByASET(meta,mos,pNam,cNam,fsc)

#%%
unose.Plot_NetGrowth_TS_Annual_FromCurrentYear_ByASET(meta,mos,pNam,cNam,fsc)
unose.Plot_Age_TS_Annual_FromCurrentYear_ByASET(meta,mos,pNam,cNam)

#%% Plot completed annual and cumulative yield
fsc='FIP'
#namFSC='All'
unose.Plot_Yield_TS_AnnAndCumu_CurrentYear(meta,mos,pNam,cNam,fsc)
unose.Plot_Yield_TS_AnnAndCumu_Completed(meta,mos,pNam,cNam)
unose.Plot_Yield_TS_AnnAndCumu_CompletedAndCAP(meta,mosWF,pNam,cNam)

#%% Disturbance and management event time series by ASET
unose.AreaAffectedByEvents_ByASET(meta,pNam,mos)

#==============================================================================
# SUMMARIZE FOR SERVICE PLAN (NOSE + FNM)
#==============================================================================

#%% Import nutrient management
pNamNM,metaNM,tvNM,mosNM,mosNM_WF,mosNM_PY,dmecNM=unm.ImportModelResults()

#%% Summarize Service Plan Progress Report
dE,dEpHa=unose.Calc_ServicePlan_ProgressReport(meta,pNam,mos,metaNM,pNamNM,mosNM)
dE

#%% Summarize Service Plan Projection
dE=unose.Calc_ServicePlan_Projection(pNam,meta,mosPY,pNamNM,metaNM,mosNM_PY)

#%% Export to FOR Climate Change Mitigation Database
unose.UpdateDatabase(meta,pNam,mos,mosWF,metaNM,pNamNM,mosNM,mosNM_WF)

#%% Emissions for current year (use for Service Plan)
unose.Plot_Emissions_TS_AnnAndCumu_CurrentYear_NOSE_AND_FNM(meta,mos,pNam,cNam,pNamNM,metaNM,mosNM)
unose.Plot_Emissions_TS_AnnAndCumu_Completed_NOSE_AND_FNM(meta,mos,pNam,cNam,pNamNM,metaNM,mosNM)
unose.Plot_Emissions_TS_AnnAndCumu_CompletedPlusCAP_NOSE_AND_FNM(meta,mosWF,pNam,cNam,pNamNM,metaNM,mosNM_WF)

#%%

















#%% QA Growth curve troubleshooting
gc1=cbu.Import_CompiledGrowthCurves(meta,pNam,[0,1]) # Nested list of: Scenario, growth curve ID, stand
iS=1812; iGC=2
plt.close('all');plt.plot(gc1[0][iGC][iS],'b-');plt.plot(gc1[1][iGC][iS],'g--')

#%% QA DMEC
iS=140
dmec[1][iS]


