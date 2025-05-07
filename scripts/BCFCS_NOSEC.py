'''
BC FOREST CARBON SUMMARY - NON-OBLIGATION STAND ESTABLISHMENT COMPLETED
'''

#%% Import Python modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import warnings
import fcgadgets.macgyver.util_general as gu
import fcgadgets.macgyver.util_gis as gis
import fcgadgets.macgyver.util_inventory as uinv
import fcgadgets.bc1ha.bc1ha_utils as u1ha
import fcgadgets.cbrunner.cbrun_util as cbu
import fcgadgets.cbrunner.cbrun as cbr
import fcgadgets.macgyver.util_fcs_graphs as ufcs
import fcgadgets.macgyver.util_fcs_qa as uqa
import fcgadgets.macgyver.util_nose as unose
import fcgadgets.macgyver.util_nm as unm
warnings.filterwarnings("ignore")
gp=gu.SetGraphics('Manuscript')

#%% Import BC1ha info
pNam='BCFCS_NOSEC'
meta=u1ha.Init()
meta['Paths'][pNam]={}
meta['Paths'][pNam]['Data']=r'C:\Data\BCFCS\BCFCS_NOSEC'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\BCFCS\BCFCS_NOSEC\2024-09-04'
meta['Graphics']['Print Figures']='On'

#%% Import project configuration
meta=cbu.ImportProjectConfig(meta,pNam)
meta[pNam]['YearCurrent']=2023

#%% Index to baseline scenarios
meta[pNam]['Project']['Baseline Indices']=np.array([0])
meta[pNam]['Project']['Actual Indices']=np.array([1])

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
meta=unose.DefineStrata(meta,pNam,dmec,lsat)

#%% Prepare project inputs 3
meta,lsat,dmec=uinv.Process3_PrepInputsByBatch(meta,pNam,lsat,dmec,gc,ugc)

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

	pNam='BCFCS_NOSEC'
	meta=gu.ipickle(r'C:\Data\BCFCS\BCFCS_NOSEC\Inputs\Metadata.pkl')
	# cbu.DeleteAllOutputFiles(meta,pNam)
	meta=cbr.MeepMeep(meta,pNam)

#%% Calculate model output statistics
cbu.Calc_MOS_GHG(meta,pNam)
cbu.Calc_MOS_Econ(meta,pNam)
cbu.Calc_MOS_Area(meta,pNam)
cbu.Calc_MOS_MortByAgent(meta,pNam)

#%% Import model results
pNam,meta,tv,mos,dmec=unose.ImportModelResults()
cNam='NOSE1'
meta['Graphics']['Print Figure Path']=r'C:\Users\rhember\OneDrive - Government of BC\Figures\BCFCS\BCFCS_NOSEC\2024-09-04'

#%% Save for Jupyter
# gu.opickle(r'C:\Data\BCFCS\BCFCS_NOSEC\Outputs\MOS.pkl',mos)

#%% Project future implementation
# Add future projected implementation
meta[pNam]['AIL CAP']=45000000/1850 # https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-investment-program/forest-investment-program-strategy-policy.pdf
mosWF=unose.ProjectFuture(meta,pNam,mos)

#%%
v='V_ToMill_MerchTotal'
iPS=np.where(meta[pNam]['Project']['Strata']['Project Type']['Unique CD']=='Salvage and Planting Post Beetle')[0]
plt.close('all')
plt.plot(np.cumsum(np.nan_to_num(mos[pNam]['Delta'][cNam]['ByStrata']['Sum'][v]['Ensemble Mean'][:,iPS,:,0])),'b-')
plt.plot(np.cumsum(np.nan_to_num(mosWF[pNam]['Delta'][cNam]['ByStrata']['Sum'][v]['Ensemble Mean'][:,iPS,:,0])),'g--')

#%% Standard QA - Calculate mean values for every stand
E_sum,E_mu=unose.QA_CalcBenefitForEachStand(meta,pNam,mos)

#%% Save summary to spreadsheet (sparse sample) for troubleshooting, investigation, QA (takes several minutes)
unose.QA_PrintSummarySparseToSpreadsheet(meta,1,dmec,E_sum)

#%% Standard QA - Plot individual stands
unose.QA_Plot_CarbonTimeSeriesByStandSelect(meta,pNam,dmec,Index=np.array([140]))

#%% Standard QA plot sample of individual stands
unose.QA_Plot_CarbonTimeSeriesByStand(meta,pNam,dmec)

#%% QA Growth curve troubleshooting
gc1=cbu.Import_CompiledGrowthCurves(meta,pNam,[0,1]) # Nested list of: Scenario, growth curve ID, stand
iS=1812; iGC=2
plt.close('all');plt.plot(gc1[0][iGC][iS],'b-');plt.plot(gc1[1][iGC][iS],'g--')

#%% QA DMEC
iS=140
dmec[1][iS]

#%% Plot time series of treatment by ASET
unose.Plot_AreaTreated_TimeSeriesByASET(meta,pNam,'NOSE',FigSize=[22,10])
unose.Plot_AreaTreated_TimeSeriesByASET(meta,pNam,'Licensees',FigSize=[22,10])
unose.Plot_AreaTreated_TimeSeriesByASET(meta,pNam,'All',FigSize=[22,10])

#%% Plot frequency of treatment by ASET
unose.Plot_AreaTreated_FrequencyByASET(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Plot frequency of treatment by funding source
unose.Plot_AreaTreated_FrequencyByFSC(meta,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unose.Plot_AreaTreated_FrequencyByFSC(meta,1960,meta[pNam]['YearCurrent']+1)

#%% Tabulate frequency by leading species (takes a few minutes)
unose.TabulateSpeciesComposition(meta,pNam,1960,meta[pNam]['YearCurrent'])
unose.TabulateSpeciesComposition(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])
unose.Plot_TreatmentFrequency_BySpecies(meta,pNam,meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent'])

#%% Tabulate frequency by burn severity class
d=unose.TabulateUnderplantingByBurnSeverityClass(meta)

#%% Tabular summary of cumulative emissions by 2050 from implementation during current year (for Service Plan Annual Progress Report)
dE,dEpHa=unose.Tabulate_CurrentYear_ForServicePlan(meta,pNam,mos)
dE
dEpHa
print(dE['Knockdown and Planting']+dE['Salvage and Planting Post Beetle']+dE['Underplanting']+dE['Fill Planting']+dE['Replanting']+dE['Ecosystem Restoration'])

#%% Plot time series for current year (use for Service Plan)
unose.Plot_EmissionsCumu_TimeSeries_FromCurrentYear(meta,mos,pNam,cNam)
unose.Plot_EmissionsAnnual_TimeSeries_FromCurrentYear(meta,mos,pNam,cNam)
unose.Plot_EmissionsCumuPerHectare_TimeSeries_FromCurrentYear(meta,mos,pNam,cNam)

#%% Plot completed annual emissions (stratified by activity type)
unose.Plot_EmissionsAnn_TimeSeries_Completed(meta,mos,pNam,cNam)
unose.Plot_EmissionsCumu_TimeSeries_Completed(meta,mos,pNam,cNam)

#%% Plot completed annual and cumulative emissions
unose.Plot_EmissionsAnnAndCumu_TimeSeries_CurrentYear(meta,mos,pNam,cNam)
unose.Plot_EmissionsAnnAndCumu_TimeSeries_Completed(meta,mos,pNam,cNam)
unose.Plot_EmissionsAnnAndCumu_TimeSeries_CompletedAndCAP(meta,mosWF,pNam,cNam)

#%%
#unose.Plot_EmissionsAnn_TimeSeries_CompletedAndCAP_WithScenarios(meta,mosWF,pNam,cNam)

def Plot_EmissionsAnnAndCumu_TimeSeries_CompletedAndCAP_WithScenarios(meta,mos,pNam,cNam):
	tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
	iT2=np.where( (tv>=1990) & (tv<=2050) )[0]
	iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']=='All')[0][0]

	cl1=[0.27,0.49,0.77]
	cl2=[0.5,0.8,0]
	xl=[1990,2050]

	plt.close('all'); fig,ax=plt.subplots(3,1,figsize=gu.cm2inch(11,11))
	ax[0].plot(tv,np.zeros(tv.size),'k-',lw=2,color=[0.85,0.85,0.85])
	#ax[0].plot([meta[pNam]['YearCurrent'],meta[pNam]['YearCurrent']],[-20,20],'k--',lw=0.5,color=[0,0,0])
	#ax[0].plot([2030,2030],[-20,20],'k--',lw=0.5,color=[0,0,0])
	#ax[0].plot([2050,2050],[-20,20],'k--',lw=0.5,color=[0,0,0])
	#ax[0].plot([2070,2070],[-20,20],'k--',lw=0.5,color=[0,0,0])

	psL=['Salvage and Planting Post Beetle','Knockdown and Planting','Road Rehabilitation','Underplanting','Replanting','Fill Planting','Ecosystem Restoration'] #'Harvest and Planting NSR Backlog'

	ysumB=np.zeros(tv.size)
	ysumP=np.zeros(tv.size)
	for nPS in psL:
		iPS=np.where(meta[pNam]['Project']['Strata']['Project Type']['Unique CD']==nPS)[0][0]
		iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']=='All')[0][0]
		yB=mos[pNam]['Scenarios'][0]['Sum']['E_Atmosphere_SubstitutionExcluded']['Ensemble Mean'][:,iPS,0,iYS]/1e6
		yP=mos[pNam]['Scenarios'][1]['Sum']['E_Atmosphere_SubstitutionExcluded']['Ensemble Mean'][:,iPS,0,iYS]/1e6
		ysumB=ysumB+np.nan_to_num(yB)
		ysumP=ysumP+np.nan_to_num(yP)
	#y=mos[pNam]['Delta'][cNam]['ByStrata']['Sum']['E_Atmosphere_SubstitutionExcluded']['Ensemble Mean'][:,0,0,iYS]/1e6
	ax[0].plot(tv[iT2],ysumB[iT2],'-',ms=3,color=cl1,mec=cl1,mfc='w',lw=2,mew=0.75,label='Baseline')
	ax[0].plot(tv[iT2],ysumP[iT2],'--',ms=3,color=cl2,mec=cl2,mfc='w',lw=2,mew=0.75,label='Actual')
	ax[0].set(xticks=np.arange(1960,2200,10),yticks=np.arange(-200,200,2),xlabel='Time, years',xlim=xl,ylim=[-3,16])
	ax[0].legend(loc='upper right',frameon=False,facecolor=None,edgecolor='w',fontsize=6)
	ax[0].yaxis.set_ticks_position('both'); ax[0].xaxis.set_ticks_position('both'); ax[0].tick_params(length=meta['Graphics']['gp']['tickl'])
	ax[0].set_ylabel('GHG emissions\n(MtCO$_2$e yr$^{-1}$)',color='k',weight='normal',fontsize=8)

	ax[1].plot(tv,np.zeros(tv.size),'k-',lw=2,color=[0.85,0.85,0.85])
	ysum=np.zeros(tv.size)
	for nPS in psL:
		iPS=np.where(meta[pNam]['Project']['Strata']['Project Type']['Unique CD']==nPS)[0][0]
		iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']=='All')[0][0]
		y=mos[pNam]['Delta'][cNam]['ByStrata']['Sum']['E_Atmosphere_SubstitutionExcluded']['Ensemble Mean'][:,iPS,0,iYS]/1e6
		ysum=ysum+np.nan_to_num(y)
	ax[1].plot(tv[iT2],ysum[iT2],'-',ms=3,color=[0.5,0,1],mec=cl2,mfc='w',lw=2,mew=0.75,label='Annual')
	ax[1].set(xticks=np.arange(1960,2200,10),yticks=np.arange(-200,200,1),xlabel='Time, years',xlim=xl,ylim=[-3.5,1])
	ax[1].yaxis.set_ticks_position('both'); ax[1].xaxis.set_ticks_position('both'); ax[1].tick_params(length=meta['Graphics']['gp']['tickl'])
	ax[1].set_ylabel('Total direct GHG\nimpact (MtCO$_2$e yr$^{-1}$)',color='k',weight='normal',fontsize=8)

	ax[2].plot(tv,np.zeros(tv.size),'k-',lw=2,color=[0.85,0.85,0.85])
	ax[2].plot(tv[iT2],ysum[iT2],'-',ms=3,color=[0.5,0,1],mec=cl2,mfc='w',lw=2,mew=0.75,label='Total direct impact')
	iRL=np.where( (tv>=2008) & (tv<=2017) )
	RL=np.ones(tv.size)*np.mean(ysum[iRL])
	iT3=np.where( (tv>=2017) )
	ax[2].plot(tv[iT2],RL[iT2],'--',ms=3,color=[0.5,0.5,0.5],mec=cl2,mfc='w',lw=2,mew=0.75,label='Reference level (2008-2017 mean)')
	ax[2].fill_between(tv[iT3],ysum[iT3],RL[iT3],color=[1,1,0.5],alpha=0.3,lw=0,label='Incremental impact')
	ax[2].set(xticks=np.arange(1960,2200,10),yticks=np.arange(-200,200,1),xlabel='Time, years',xlim=xl,ylim=[-3.5,1])
	ax[2].yaxis.set_ticks_position('both'); ax[2].xaxis.set_ticks_position('both'); ax[2].tick_params(length=meta['Graphics']['gp']['tickl'])
	ax[2].set_ylabel('Incremental GHG\nimpact (MtCO$_2$e yr$^{-1}$)',color='k',weight='normal',fontsize=8)
	ax[2].legend(loc='lower left',frameon=False,facecolor=None,edgecolor='w',fontsize=6)
	gu.axletters(ax,plt,0.02,0.87,FontColor=meta['Graphics']['gp']['cla'],LetterStyle=meta['Graphics']['Modelling']['AxesLetterStyle'],FontWeight=meta['Graphics']['Modelling']['AxesFontWeight'])

	plt.tight_layout()
	if meta['Graphics']['Print Figures']=='On':
		gu.PrintFig(meta['Graphics']['Print Figure Path'] + '\\EmissionsAnnAndCumu_TimeSeries_CompletedAndCAP_WithScenarios','png',900)
	return
Plot_EmissionsAnnAndCumu_TimeSeries_CompletedAndCAP_WithScenarios(meta,mosWF,pNam,cNam)

#%% Plot completed annual and cumulative yield
unose.Plot_YieldAnnAndCumu_TimeSeries_Completed(meta,mos,pNam,cNam)
unose.Plot_YieldAnnAndCumu_TimeSeries_CompletedAndCAP(meta,mosWF,pNam,cNam)

#%% Plot time series of area treated by project type (from model output)
#unose.Plot_AIL_NOSE_ByProjectType_FromModel(meta,pNam,mos,tv,1)

#%% Import nutrient management
pNamNM,metaNM,tvNM,mosNM,mosNM_WF,dmecNM=unm.ImportModelResults()

unose.Plot_EmissionsAnnAndCumu_TimeSeries_Completed_WithNM(meta,mos,mosNM,pNam)
unose.Plot_EmissionsAnnAndCumu_TimeSeries_CompletedAndCAP_WithNM(meta,mosWF,mosNM_WF,pNam)

#%% Service Plan Projection
mosNO_SPP=unose.ProjectServicePlan(meta,pNam,mos)
unose.Plot_EmissionsAnnAndCumu_TimeSeries_ServicePlanProjectionYear(meta,mosNO_SPP,pNam)

mosNM_SPP=unm.ProjectServicePlan(metaNM,pNamNM,mosNM)
unose.Plot_EmissionsAnnAndCumu_TimeSeries_ServicePlanProjectionYear_WithNM(meta,mosNO_SPP,mosNM_SPP,pNam)

#%% Export to FOR Climate Change Mitigation Database
unose.UpdateDatabase(meta,pNam,mos,mosWF,metaNM,pNamNM,mosNM,mosNM_WF)

#%% Plot summary time series for specific strata
tv=np.arange(meta[pNam]['Project']['Year Start Saving'],meta[pNam]['Project']['Year End']+1,1)
#dI=gu.ipickle(r'C:\Data\BC1ha\RSLT_ACTIVITY_TREATMENT_SVW\ASET_SummaryByTime.pkl')
#iT=np.where(dI['tv']==YearCurrent)[0]
#A_Treat=dI['A NOSE'][iT[0],:]
#cd=list(meta['LUT']['Derived']['ASET'].keys())

iB=0;iP=1
cd0='Salvage and Planting Post Beetle'

operS='Mean'
#v='E_Atmosphere_SubstitutionExcluded_Cumulative'
#v='C_Biomass'
#v='C_Litter'
#v='C_DeadWood'
#v='C_ToPileBurnTot'
#v='C_ToMillTotal'
#v='C_Felled'
#v='E_Domestic_ForestSector_OpenBurning'
v='E_Domestic_ForestSector_Wildfire'
#v='C_G_Gross'
#v='C_G_Net_Reg'

iPS=np.where(meta[pNam]['Project']['Strata']['Project Type']['Unique CD']==cd0)[0][0]
iSS=np.where(meta[pNam]['Project']['Strata']['Spatial']['Unique CD']=='All')[0][0]
iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']==str(meta[pNam]['YearCurrent']))[0][0]
y0=mos[pNam]['Scenarios'][iB][operS][v]['Ensemble Mean'][:,iPS,iSS,iYS]
y1=mos[pNam]['Scenarios'][iP][operS][v]['Ensemble Mean'][:,iPS,iSS,iYS]
plt.close('all')
plt.plot(tv,y0,'ob-')
plt.plot(tv,y1,'og--')

# y0=mos[pNam]['Delta']['NOSE1']['ByStrata']['Sum'][v]['Ensemble Mean'][:,iPS,iSS,iYS]
# plt.close('all')
# plt.plot(tv,y0,'b-')
# plt.plot(tv,y1,'g--')

#%% Specify results inclusion
# pNam=pNam
# #psL=['Road Rehabilitation','Underplanting','Straight-to-planting Post Beetles','Replanting']# 'Harvest and Planting NSR Backlog','Salvage and Planting','Knockdown and Planting',
# psL=['Underplanting']
# for nPS in psL: #meta[pNam]['Project']['Strata']['Project Type']['Unique CD']:
# 	nSS='All';nYS='All'
# 	iSS=np.where(meta[pNam]['Project']['Strata']['Spatial']['Unique CD']==nSS)[0][0]
# 	iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']==nYS)[0][0]
# 	iPS=np.where(meta[pNam]['Project']['Strata']['Project Type']['Unique CD']==nPS)[0][0]

# 	dR={}
# 	dR['Area_DisturbedAndManaged']='On'
# 	dR['Area_HarvestTimeSeries']='On'
# 	dR['Area_THLB_TimeSeries']='Off'
# 	dR['GHGBalance']='On'
# 	dR['GHGBalanceSimple']='On'
# 	dR['CarbonFluxTimeSeries']='On'
# 	dR['CarbonPoolBarChart']='On'
# 	dR['CarbonFluxesBarChart']='On'
# 	dR['CarbonFluxMortality']='On'
# 	dR['HarvestVolumeTimeSeries']='On'
# 	dR['HarvestVolumePerHectareTimeSeries']='On'
# 	dR['AgeClassDist']='On'
# 	dR['MortalitySpectrum']='On'
# 	dR['NetGrowthTimeSeries']='Off'
# 	dR['ComparisonWithPIR']='On'
# 	dR['WildfireProbHistTimeSeries']='Off'
# 	#dR['Summary of Approaches']='Off'
# 	dR['AllVariableTimeSeries']='Off'
# 	dR['SaveTabData']='Off'
# 	dR['Map Status']='Off'
# 	dR['Map Time Period']=[2011,2020]

# 	dR['ScenarioComp_GHGBalanceAnnual']='On'
# 	dR['ScenarioComp_GHGBalanceAnnualPlusCumu']='On'
# 	dR['ScenarioComp_ForcingBarChart']='On'

# 	dR['EvalAtPlots_BiomassDynamicsAve_CN']='Off'
# 	dR['EvalAtPlots_AgeByBGCZ_CNV']='Off'
# 	dR['EvalAtPlots_BiomassByBGC_CNV']='Off'
# 	dR['EvalAtPlots_GrossGrowthByBGC_CN']='Off'
# 	dR['EvalAtPlots_MortalityByBGC_CN']='Off'
# 	dR['EvalAtPlots_SOCByBGC_ShawComp']='Off'
# 	dR['EvalAtPlots_AgeResponsesBiomassAndNetGrowth_ByReg_CN']='Off'
# 	dR['EvalAtPlots_AgeResponsesGrossGrowthAndMortality_ByReg']='Off'
# 	dR['QA Profile IBM']='Off'
# 	dR['QA Profile Wildfire']='Off'
# 	dR['Export MOS Strata to DB']='Off'
# 	dH_ByBGCZ=[]
# 	ufcs.RunOutputGraphics(meta,pNam,cNam,mos,dR,iPS,iSS,iYS,tv,iT,[],dH_ByBGCZ)






# #%% Tabular summaries
# vL=['C_Biomass_Tot','C_DeadWood_Tot','C_Litter_Tot','C_Soil_Tot','C_HWP_Tot','C_Geological_Tot']
# df=ufcs.ExportTableScenariosAndDelta(meta,pNam,mos,cnam='NOSE1',table_name='Pools',oper='Sum',t0=2021,t1=2030,iPS=0,iSS=0,iYS=0,units='Actual',multi=1e-6,save='Off',variables=vL)
# df

# vL=['E_CO2e_LULUCF_NPP','E_CO2e_LULUCF_RH','E_CO2e_LULUCF_OpenBurning','E_CO2e_LULUCF_Wildfire','E_CO2e_LULUCF_Other','E_CO2e_LULUCF_Denit','E_CO2e_LULUCF_HWP','E_CO2e_OperForTot',
# 	'E_CO2e_SUB_E','E_CO2e_SUB_M','E_CO2e_AGHGB_WOSub','E_CO2e_AGHGB_WSub']
# df=ufcs.ExportTableScenariosAndDelta(meta,pNam,mos,cnam='NOSE1',table_name='Pools',oper='Sum',t0=2021,t1=2030,iPS=0,iSS=0,iYS=0,units='Actual',multi=1e-6,save='Off',variables=vL)
# df

# vL=['E_CO2e_LULUCF_NPP','E_CO2e_LULUCF_RH','E_CO2e_LULUCF_OpenBurning','E_CO2e_LULUCF_Wildfire','E_CO2e_LULUCF_Other','E_CO2e_LULUCF_Denit','E_CO2e_LULUCF_HWP','E_CO2e_OperForTot',
# 	'E_CO2e_SUB_E','E_CO2e_SUB_M','E_CO2e_AGHGB_WOSub','E_CO2e_AGHGB_WSub']
# df=ufcs.ExportTableScenariosAndDelta(meta,pNam,mos,cnam='NOSE1',table_name='Pools',oper='Sum',t0=2021,t1=2100,iPS=0,iSS=0,iYS=0,units='Actual',multi=1e-6,save='Off',variables=vL)
# df

# vL=['V_MerchDead','V_MerchLive','V_MerchTotal','V_ToMillMerchDead','V_ToMillMerchLive','V_ToMillMerchTotal','V_ToMillNonMerch']
# df=ufcs.ExportTableScenariosAndDelta(meta,pNam,mos,cnam='NOSE1',table_name='Pools',oper='Sum',t0=2021,t1=2100,iPS=0,iSS=0,iYS=0,units='Actual',multi=1e-6,save='Off',variables=vL)
# df

# vL=['Cost Total','Cost Total Disc','Cost Silviculture Total','Cost Silviculture Total Disc','Revenue Gross','Revenue Gross Disc','Revenue Net','Revenue Net Disc']
# df=ufcs.ExportTableScenariosAndDelta(meta,pNam,mos,cnam='NOSE1',table_name='Pools',oper='Sum',t0=2021,t1=2100,iPS=0,iSS=0,iYS=0,units='Actual',multi=1e-6,save='Off',variables=vL)
# df

# list(mos[pNam]['Delta']['NOSE1']['ByStrata']['Mean'].keys())

# #%%

# plt.close('all')
# iScn=1
# plt.plot(tv,mos[pNam]['Scenarios'][iScn]['Sum']['Area_Planting']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNam]['Project']['AEF'],'-bo')

# plt.close('all')
# plt.plot(tv,mos[pNamF]['Scenarios'][0]['Sum']['Area_Harvest']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNamF]['Project']['AEF'],'-bo')
# plt.plot(tv,mos[pNamF]['Scenarios'][1]['Sum']['Area_Harvest']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNamF]['Project']['AEF'],'-gs')

# plt.close('all')
# plt.plot(tv,mos[pNam]['Delta'][cNam]['ByStrata']['Sum']['E_CO2e_AGHGB_WSub']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNam]['Project']['AEF']/1e6,'-bo')
# plt.plot(tv,mos[pNamF]['Delta'][cNam]['ByStrata']['Sum']['E_CO2e_AGHGB_WSub']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNamF]['Project']['AEF']/1e6,'-gs')

# plt.close('all')
# plt.plot(tv,mos[pNam]['Delta'][cNam]['ByStrata']['Sum']['V_ToMillMerchTotal']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNam]['Project']['AEF']/1e6,'-bo')
# plt.plot(tv,mos[pNamF]['Delta'][cNam]['ByStrata']['Sum']['V_ToMillMerchTotal']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNamF]['Project']['AEF']/1e6,'-gs')

# np.sum(mos[pNam]['Scenarios'][iScn]['Sum']['Area_Fertilization Aerial']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNam]['Project']['AEF'])




# #%%
# iScn=1
# iSS=np.where(meta[pNam]['Project']['Strata']['Spatial']['Unique CD']==nSS)[0][0]
# iYS=np.where(meta[pNam]['Project']['Strata']['Year']['Unique CD']==nYS)[0][0]

# plt.close('all')
# nPS='Underplanting';nSS='All';nYS='All'
# #nPS='Harvest and Planting NSR Backlog';nSS='All';nYS='All'
# #nPS='Salvage and Planting';nSS='All';nYS='All'
# iPS=np.where(meta[pNam]['Project']['Strata']['Project Type']['Unique CD']==nPS)[0][0]
# plt.plot(tv,mos[pNam]['Scenarios'][iScn]['Sum']['Area_Planting']['Ensemble Mean'][:,iPS,iSS,iYS]*meta[pNam]['Project']['AEF'],'-bo')




