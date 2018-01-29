#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 24 13:59:00 2017

@author: zdhughes
"""

#         MASTER FILE                            CHILD FILE
#############################          #############################
#[General]                  #          # [StageConfig]             #
#>Options                   #          # >settings                 #
#                           #          #                           #
#[Sections]                 #          #                           #
#>selections                #          #                           #
#                           #          #                           #
#[Selection]                #          #                           #
#>stages                    #          #                           #
#                           #          #                           #
#[SelectionConfig]          #          #                           #
#>parameters                #          #                           #
#                           #          #                           #
#                           #          #                           #
#############################          #############################

import general_functions_fermi as GFF
from configparser import ConfigParser, ExtendedInterpolation
import subprocess
import sys
import code
import os
import numpy as np
from collections import OrderedDict as od

#This class object should hold all the info for a "top" stage. I.e. "Main"+"MainConfig"+the main child config.
#It gets passed the masterConfig OBJECT and a name of a section within that config object.
#It pulls out that section and the section+"config" section and packages it as a single object.
class runlistMember():
	
	"""This holds all the information related to a particular run as defined in the master configuration file."""
	
	def __init__(self, masterConfig = None, selectionName = None, c = None):
		
		"""Loads in the two related sections from the master configuration file and loads in the child config file
		that holds all the parameters."""
		
		self.masterConfig = masterConfig if masterConfig is not None else sys.exit('No master config file provided.')
		self.selectionName = selectionName if selectionName is not None else sys.exit('No top section to load provided.')
		self.c = c if c is not None else GFF.colors()
		self.selectionConfigName = self.selectionName+'Config'

		#From master:
		#[General] options -> general
		#The selection options -> stages
		#the selection config options -> selection config
		self.general = od(self.masterConfig.items('General'))
		self.stages = od(self.masterConfig.items(self.selectionName))
		self.parameters = od(self.masterConfig.items(self.selectionConfigName))

		#code.interact(local=locals())
		#sys.exit('Code Break!')	
		
		#Cast the above into the correct types.
		for key in self.general:
			self.general[key] = GFF.tryeval(self.general[key])
		for stage in self.stages:
			self.stages[stage] = GFF.tryeval(self.stages[stage])	
		for parameter in self.parameters:
			self.parameters[parameter] = GFF.tryeval(self.parameters[parameter])

		#Read in the child config, as defined in the selection config. DO NOT cast them as types, since they will be written out to files.
		self.childConfig = ConfigParser(interpolation=ExtendedInterpolation(),inline_comment_prefixes=('#'))
		self.childConfig.optionxform = str
		self.childConfig.read(self.parameters['config'])
			
	def printInfo(self):
		print('Printing selection '+self.c.green(self.selectionName))
		for stage in self.stages:
			if self.stages[stage] == True:
				print(self.c.lightgreen(stage)+' : '+self.c.lightblue(self.stages[stage]))
			else:
				print(self.c.lightgreen(stage)+' : '+self.c.lightred(self.stages[stage]))

		print(self.c.orange('------------------------------'))
		
		print('Printing selection config '+self.c.green(self.selectionConfigName))
		for parameter in self.parameters:
			print(self.c.lightgreen(parameter)+' : '+self.c.lightblue(self.parameters[parameter]))
		
		print(self.c.orange('------------------------------'))

		print('Printing section fermi parameters from file '+self.c.yellow(self.parameters['config']))
		for stageConfig in self.childConfig:
			if stageConfig != 'DEFAULT':			
				print('Printing stageConfig '+self.c.green(stageConfig))
				for setting in self.childConfig[stageConfig]:
					print(self.c.lightgreen(setting)+' : '+self.c.lightblue(self.childConfig[stageConfig][setting]))
				print(self.c.gray('++++++++++++++++++++++++++++++'))
				
	def printSection(self, stageConfig):
		print('Printing settings for stage-config '+self.c.green(stageConfig))
		for setting in self.childConfig[stageConfig]:
			print(self.c.lightgreen(setting)+' : '+self.c.lightblue(self.childConfig[stageConfig][setting]))
		
	def getChild(self):
		return self.childConfig
	def getSettings(self, stageConfig):
		return od(self.childConfig.items(stageConfig))


class fermiRunlistMember(runlistMember):
	
	def __init__(self, masterConfig = None, selectionName = None, c = None):
		runlistMember.__init__(self, masterConfig, selectionName, c)
		self.getDefaults()
		if self.parameters['deltaT'] != 'NOPASS':
			self.range = np.arange(int(self.parameters['startTime']), int(self.parameters['stopTime']), int(self.parameters['deltaT']))
			self.times = list(zip(self.range[:-1],self.range[1:]))
			self.saveName = [self.general['saveNameStem']+'_'+str(x[0]) for x in self.times]	
		else:
			self.range = [self.selectionName]
			self.times = [(int(self.parameters['startTime']),int(self.parameters['stopTime']))]
			self.saveName = self.general['saveNameStem']+'_'+self.selectionName
			
	def __iter__(self):
		return iter(self.times)
			
	def getDefaults(self):
		
		self.doFilterFlag = {'infile':False,'outfile':False}
		self.doMaketimeFlag = {'scfile':False, 'evfile':False, 'outfile':False}
		self.doModelFlag = {'infile':False,'outfile':False, 'wd':False}		
		self.doTempoFlag = {'infile':False,'scfile':False,'outfile':False}
		self.doFoldFlag = {'infile':False,'outfile':False}
		self.doSortFlag = {'infile':False, 'scfile':False, 'outfile':False}
		self.doCmapFlag = {'evfile':False,'scfile':False,'outfile':False}
		self.doCCUBEFlag = {'evfile':False,'scfile':False,'outfile':False}
		self.doLivetimeFlag = {'evfile':False, 'scfile':False, 'outfile':False}
		self.doExposureFlag = {'infile':False, 'cmap':False, 'outfile':False}
		self.doSrcFlag = {'scfile':False, 'expcube':False, 'cmap':False, 'srcmdl':False,'bexpmap':False, 'outfile':False}
		self.doLikeFlag = {'expcube':False, 'srcmdl':False, 'sfile':False, 'results':False, 'specfile':False, 'evfile':False, 'scfile':False, 'cmap':False, 'bexpmap':False, 'emin':False, 'emax':False}
		self.doModelMapFlag = {'srcmaps':False, 'srcmdl':False, 'outfile':False, 'expcube':False, 'bexpmap':False}
		self.doResidualFlag = {'infile1':False, 'infile2':False, 'outfile':False}

		self.doFilterFlag['infile'] = True if self.childConfig['doFilter']['infile'] == 'NOPASS' else self.childConfig['doFilter']['infile']
		self.doFilterFlag['outfile'] = True if self.childConfig['doFilter']['outfile'] == 'NOPASS' else self.childConfig['doFilter']['outfile']

		self.doMaketimeFlag['scfile'] = True if self.childConfig['doMaketime']['scfile'] == 'NOPASS' else self.childConfig['doMaketime']['scfile']
		self.doMaketimeFlag['evfile'] = True if self.childConfig['doMaketime']['evfile'] == 'NOPASS' else self.childConfig['doMaketime']['evfile']
		self.doMaketimeFlag['outfile'] = True if self.childConfig['doMaketime']['outfile'] == 'NOPASS' else self.childConfig['doMaketime']['outfile']
		
		self.doModelFlag['infile'] = True if self.childConfig['doModel']['infile'] == 'NOPASS' else self.childConfig['doModel']['infile']
		self.doModelFlag['outfile'] = True if self.childConfig['doModel']['outfile'] == 'NOPASS' else self.childConfig['doModel']['outfile']
		self.doModelFlag['wd'] = True if self.childConfig['doModel']['wd'] == 'NOPASS' else self.childConfig['doModel']['wd']
		
		self.doTempoFlag['infile'] = True if self.childConfig['doTempo']['infile'] == 'NOPASS' else self.childConfig['doTempo']['infile']
		self.doTempoFlag['scfile'] = True if self.childConfig['doTempo']['scfile'] == 'NOPASS' else self.childConfig['doTempo']['scfile']
		self.doTempoFlag['outfile'] = True if self.childConfig['doTempo']['outfile'] == 'NOPASS' else self.childConfig['doTempo']['outfile']
		
		self.doFoldFlag['infile'] = True if self.childConfig['doFold']['infile'] == 'NOPASS' else self.childConfig['doFold']['infile']
		self.doFoldFlag['outfile'] = True if self.childConfig['doFold']['outfile'] == 'NOPASS' else self.childConfig['doFold']['outfile']
		
		self.doSortFlag['infile'] = True if self.childConfig['doSort']['infile'] == 'NOPASS' else self.childConfig['doSort']['infile']
		self.doSortFlag['scfile'] = True if self.childConfig['doSort']['scfile'] == 'NOPASS' else self.childConfig['doSort']['scfile']
		self.doSortFlag['outfile'] = True if self.childConfig['doSort']['outfile'] == 'NOPASS' else self.childConfig['doSort']['outfile']
		
		self.doCmapFlag['evfile'] = True if self.childConfig['doCmap']['evfile'] == 'NOPASS' else self.childConfig['doCmap']['evfile']
		self.doCmapFlag['scfile'] = True if self.childConfig['doCmap']['scfile'] == 'NOPASS' else self.childConfig['doCmap']['scfile']
		self.doCmapFlag['outfile'] = True if self.childConfig['doCmap']['outfile'] == 'NOPASS' else self.childConfig['doCmap']['outfile']
		
		self.doCCUBEFlag['evfile'] = True if self.childConfig['doCCUBE']['evfile'] == 'NOPASS' else self.childConfig['doCCUBE']['evfile']
		self.doCCUBEFlag['scfile'] = True if self.childConfig['doCCUBE']['scfile'] == 'NOPASS' else self.childConfig['doCCUBE']['scfile']
		self.doCCUBEFlag['outfile'] = True if self.childConfig['doCCUBE']['outfile'] == 'NOPASS' else self.childConfig['doCCUBE']['outfile']
		
		self.doLivetimeFlag['evfile'] = True if self.childConfig['doLivetime']['evfile'] == 'NOPASS' else self.childConfig['doLivetime']['evfile']
		self.doLivetimeFlag['scfile'] = True if self.childConfig['doLivetime']['scfile'] == 'NOPASS' else self.childConfig['doLivetime']['scfile']
		self.doLivetimeFlag['outfile'] = True if self.childConfig['doLivetime']['outfile'] == 'NOPASS' else self.childConfig['doLivetime']['outfile']
		
		self.doExposureFlag['infile'] = True if self.childConfig['doExposure']['infile'] == 'NOPASS' else self.childConfig['doExposure']['infile']
		self.doExposureFlag['cmap'] = True if self.childConfig['doExposure']['cmap'] == 'NOPASS' else self.childConfig['doExposure']['cmap']
		self.doExposureFlag['outfile'] = True if self.childConfig['doExposure']['outfile'] == 'NOPASS' else self.childConfig['doExposure']['outfile']
		
		self.doSrcFlag['scfile'] = True if self.childConfig['doSrc']['scfile'] == 'NOPASS' else self.childConfig['doSrc']['scfile']
		self.doSrcFlag['expcube'] = True if self.childConfig['doSrc']['expcube'] == 'NOPASS' else self.childConfig['doSrc']['expcube']
		self.doSrcFlag['cmap'] = True if self.childConfig['doSrc']['cmap'] == 'NOPASS' else self.childConfig['doSrc']['cmap']
		self.doSrcFlag['srcmdl'] = True if self.childConfig['doSrc']['srcmdl'] == 'NOPASS' else self.childConfig['doSrc']['srcmdl']
		self.doSrcFlag['bexpmap'] = True if self.childConfig['doSrc']['bexpmap'] == 'NOPASS' else self.childConfig['doSrc']['bexpmap']
		self.doSrcFlag['outfile'] = True if self.childConfig['doSrc']['outfile'] == 'NOPASS' else self.childConfig['doSrc']['outfile']

		self.doLikeFlag['srcmap'] = True if self.childConfig['doLike']['srcmap'] == 'NOPASS' else self.childConfig['doLike']['srcmap']
		self.doLikeFlag['expcube'] = True if self.childConfig['doLike']['expcube'] == 'NOPASS' else self.childConfig['doLike']['expcube']		
		self.doLikeFlag['bexpmap'] = True if self.childConfig['doLike']['bexpmap'] == 'NOPASS' else self.childConfig['doLike']['bexpmap']
		self.doLikeFlag['srcmdl'] = True if self.childConfig['doLike']['srcmdl'] == 'NOPASS' else self.childConfig['doLike']['srcmdl']
		self.doLikeFlag['outmodel'] = True if self.childConfig['doLike']['outmodel'] == 'NOPASS' else self.childConfig['doLike']['outmodel']
		self.doLikeFlag['results'] = True if self.childConfig['doLike']['results'] == 'NOPASS' else self.childConfig['doLike']['results']
		self.doLikeFlag['specfile'] = True if self.childConfig['doLike']['specfile'] == 'NOPASS' else self.childConfig['doLike']['specfile']
		self.doLikeFlag['emin'] = True if self.childConfig['doLike']['emin'] == 'NOPASS' else self.childConfig['doLike']['emin']
		self.doLikeFlag['emax'] = True if self.childConfig['doLike']['emax'] == 'NOPASS' else self.childConfig['doLike']['emax']

		self.doModelMapFlag['srcmaps'] = True if self.childConfig['doModelMap']['srcmaps'] == 'NOPASS' else self.childConfig['doModelMap']['srcmaps']
		self.doModelMapFlag['srcmdl'] = True if self.childConfig['doModelMap']['srcmdl'] == 'NOPASS' else self.childConfig['doModelMap']['srcmdl']
		self.doModelMapFlag['outfile'] = True if self.childConfig['doModelMap']['outfile'] == 'NOPASS' else self.childConfig['doModelMap']['outfile']
		self.doModelMapFlag['expcube'] = True if self.childConfig['doModelMap']['expcube'] == 'NOPASS' else self.childConfig['doModelMap']['expcube']
		self.doModelMapFlag['bexpmap'] = True if self.childConfig['doModelMap']['bexpmap'] == 'NOPASS' else self.childConfig['doModelMap']['bexpmap']

		self.doResidualFlag['infile1'] = True if self.childConfig['doResidual']['infile1'] == 'NOPASS' else self.childConfig['doResidual']['infile1']
		self.doResidualFlag['infile2'] = True if self.childConfig['doResidual']['infile2'] == 'NOPASS' else self.childConfig['doResidual']['infile2']
		self.doResidualFlag['outfile'] = True if self.childConfig['doResidual']['outfile'] == 'NOPASS' else self.childConfig['doResidual']['outfile']
					
	def setDefaults(self, inter = 'main', likemodel='', increment=''):

		directory = self.parameters['directory']
		defaultStem = directory+self.general['saveNameStem']
		modelDir = self.parameters['modelDir']
		modelStem = modelDir+self.general['saveNameStem']
		if increment:
			interIncrement = inter+'_'+str(increment)
		else:
			interIncrement = inter
		
		self.childConfig['doFilter']['infile'] = self.general['runlistFile'] if self.doFilterFlag['infile'] == True else self.doFilterFlag['outfile']
		self.childConfig['doFilter']['outfile'] = defaultStem+'_'+str(interIncrement)+'_filter.fits' if self.doFilterFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doFilterFlag['outfile']+'.fits'

		self.childConfig['doMaketime']['scfile'] = self.general['spacecraftFile'] if self.doMaketimeFlag['scfile'] == True else self.doMaketimeFlag['scfile']
		self.childConfig['doMaketime']['evfile'] = defaultStem+'_'+str(interIncrement)+'_filter.fits' if self.doMaketimeFlag['evfile'] == True else defaultStem+'_'+str(interIncrement)+self.doMaketimeFlag['evfile']+'.fits'
		self.childConfig['doMaketime']['outfile'] = defaultStem+'_'+str(interIncrement)+'_gti.fits' if self.doMaketimeFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doMaketimeFlag['outfile']+'.fits'
		
		self.childConfig['doModel']['infile'] = defaultStem+'_'+str(interIncrement)+'_gti.fits' if self.doModelFlag['infile'] == True else defaultStem+'_'+str(interIncrement)+self.doModelFlag['infile']+'.fits'
		self.childConfig['doModel']['outfile'] = modelStem+'_'+str(interIncrement)+str(likemodel)+'_model.xml' if self.doModelFlag['outfile'] == True else modelStem+'_'+str(interIncrement)+str(likemodel)+self.doModelFlag['outfile']+'.xml'
		self.childConfig['doModel']['wd'] = modelDir if self.doModelFlag['wd'] == True else self.doModelFlag['wd']
		
		self.childConfig['doTempo']['infile'] = defaultStem+'_'+str(interIncrement)+'_gti.fits' if self.doTempoFlag['infile'] == True else defaultStem+'_'+str(interIncrement)+self.doTempoFlag['infile']+'.fits'
		self.childConfig['doTempo']['scfile'] = self.general['spacecraftFile']if self.doTempoFlag['scfile'] == True else self.doTempoFlag['scfile']
		self.childConfig['doTempo']['outfile'] = defaultStem+'_'+str(interIncrement)+'_phasecuts.fits'if self.doTempoFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doTempoFlag['outfile']+'.fits'
		
		self.childConfig['doFold']['infile'] = defaultStem+'_'+str(interIncrement)+'_phasecuts.fits' if self.doFoldFlag['infile'] == True else defaultStem+'_'+str(interIncrement)+self.doFoldFlag['infile']+'.fits'
		self.childConfig['doFold']['outfile'] = defaultStem+'_'+str(interIncrement)+'_binary.fits' if self.doFoldFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doFoldFlag['outfile']+'.fits'
		
		self.childConfig['doSort']['infile'] = defaultStem+'_'+str(interIncrement)+'_phasecuts.fits' if self.doSortFlag['infile'] == True else defaultStem+'_'+str(interIncrement)+self.doSortFlag['infile']+'.fits'
		self.childConfig['doSort']['scfile'] = self.general['spacecraftFile'] if self.doSortFlag['scfile'] == True else self.doSortFlag['scfile']
		self.childConfig['doSort']['outfile'] = defaultStem+'_'+str(interIncrement)+'_sorted.fits' if self.doSortFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doSortFlag['outfile']+'.fits'
		
		self.childConfig['doCmap']['evfile'] = defaultStem+'_'+str(interIncrement)+'_binary.fits' if self.doCmapFlag['evfile'] == True else defaultStem+'_'+str(interIncrement)+self.doCmapFlag['evfile']+'.fits'
		self.childConfig['doCmap']['scfile'] = self.general['spacecraftFile'] if self.doCmapFlag['scfile'] == True else self.doCmapFlag['scfile']
		self.childConfig['doCmap']['outfile'] = defaultStem+'_'+str(interIncrement)+'_cmap.fits' if self.doCmapFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doCmapFlag['outfile']+'.fits'
		
		self.childConfig['doCCUBE']['evfile'] = defaultStem+'_'+str(interIncrement)+'_binary.fits' if self.doCCUBEFlag['evfile'] == True else defaultStem+'_'+str(interIncrement)+self.doCCUBEFlag['evfile']+'.fits'
		self.childConfig['doCCUBE']['scfile'] = self.general['spacecraftFile'] if self.doCCUBEFlag['scfile'] == True else self.doCCUBEFlag['scfile']
		self.childConfig['doCCUBE']['outfile'] = defaultStem+'_'+str(interIncrement)+'_ccube.fits' if self.doCCUBEFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doCCUBEFlag['outfile']+'.fits'
		
		self.childConfig['doLivetime']['evfile'] = defaultStem+'_'+str(interIncrement)+'_binary.fits' if self.doLivetimeFlag['evfile'] == True else defaultStem+'_'+str(interIncrement)+self.doLivetimeFlag['evfile']+'.fits'
		self.childConfig['doLivetime']['scfile'] = self.general['spacecraftFile'] if self.doLivetimeFlag['scfile'] == True else self.doLivetimeFlag['scfile']
		self.childConfig['doLivetime']['outfile'] = defaultStem+'_'+str(interIncrement)+'_livetime.fits' if self.doLivetimeFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doLivetimeFlag['outfile']+'.fits'
		
		self.childConfig['doExposure']['infile'] = defaultStem+'_'+str(interIncrement)+'_livetime.fits' if self.doExposureFlag['infile'] == True else defaultStem+'_'+str(interIncrement)+self.doExposureFlag['infile']+'.fits'
		self.childConfig['doExposure']['cmap'] = defaultStem+'_'+str(interIncrement)+'_ccube.fits' if self.doExposureFlag['cmap'] == True else defaultStem+'_'+str(interIncrement)+self.doExposureFlag['cmap']+'.fits'
		self.childConfig['doExposure']['outfile'] = defaultStem+'_'+str(interIncrement)+'_exposure.fits' if self.doExposureFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+self.doExposureFlag['outfile']+'.fits'
		
		self.childConfig['doSrc']['scfile'] = self.general['spacecraftFile'] if self.doSrcFlag['scfile'] == True else self.doSrcFlag['scfile']
		self.childConfig['doSrc']['expcube'] = defaultStem+'_'+str(interIncrement)+'_livetime.fits' if self.doSrcFlag['expcube'] == True else defaultStem+'_'+str(interIncrement)+self.doSrcFlag['expcube']+'.fits'
		self.childConfig['doSrc']['cmap'] = defaultStem+'_'+str(interIncrement)+'_ccube.fits' if self.doSrcFlag['cmap'] == True else defaultStem+'_'+str(interIncrement)+self.doSrcFlag['cmap']+'.fits'
		self.childConfig['doSrc']['srcmdl'] = modelStem+'_'+str(interIncrement)+str(likemodel)+'_model.xml' if self.doSrcFlag['srcmdl'] == True else self.doSrcFlag['srcmdl']
		self.childConfig['doSrc']['bexpmap'] = defaultStem+'_'+str(interIncrement)+'_exposure.fits' if self.doSrcFlag['bexpmap'] == True else defaultStem+'_'+str(interIncrement)+self.doSrcFlag['bexpmap']+'.fits'
		self.childConfig['doSrc']['outfile'] = defaultStem+'_'+str(interIncrement)+str(likemodel)+'_srcmap.fits' if self.doSrcFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+str(likemodel)+self.doSrcFlag['outfile']+'.fits'

		self.childConfig['doLike']['srcmap'] = defaultStem+'_'+str(interIncrement)+str(likemodel)+'_srcmap.fits' if self.doLikeFlag['srcmap'] == True else defaultStem+'_'+str(interIncrement)+str(likemodel)+self.doLikeFlag['srcmap']+'.fits'	
		self.childConfig['doLike']['expcube'] = defaultStem+'_'+str(interIncrement)+'_livetime.fits' if self.doLikeFlag['expcube'] == True else defaultStem+'_'+str(interIncrement)+self.doLikeFlag['expcube']+'.fits'
		self.childConfig['doLike']['bexpmap'] = defaultStem+'_'+str(interIncrement)+'_exposure.fits' if self.doLikeFlag['bexpmap'] == True else defaultStem+'_'+str(interIncrement)+self.doLikeFlag['bexpmap']+'.fits'
		self.childConfig['doLike']['srcmdl'] = modelStem+'_'+str(interIncrement)+str(likemodel)+'_model.xml' if self.doLikeFlag['srcmdl'] == True else self.doLikeFlag['srcmdl']
		self.childConfig['doLike']['outmodel'] = modelDir+'out_'+self.childConfig['doLike']['srcmdl'].split('/')[-1] if self.doLikeFlag['outmodel'] == True else self.doLikeFlag['outmodel']
		self.childConfig['doLike']['results'] = defaultStem+'_'+str(interIncrement)+str(likemodel)+'_results.dat' if self.doLikeFlag['results'] == True else defaultStem+'_'+str(interIncrement)+str(likemodel)+self.doLikeFlag['results']+'.dat'
		self.childConfig['doLike']['specfile'] = defaultStem+'_'+str(interIncrement)+str(likemodel)+'_spec.fits' if self.doLikeFlag['specfile'] == True else defaultStem+'_'+str(interIncrement)+str(likemodel)+self.doLikeFlag['specfile']+'.fits'
		self.childConfig['doLike']['emin'] = '100' if self.doLikeFlag['emin'] == True else self.doLikeFlag['emin']
		self.childConfig['doLike']['emax'] = '300000' if self.doLikeFlag['emax'] == True else self.doLikeFlag['emax']

		self.childConfig['doModelMap']['srcmaps'] = defaultStem+'_'+str(interIncrement)+str(likemodel)+'_srcmap.fits' if self.doModelMapFlag['srcmaps'] == True else defaultStem+'_'+str(interIncrement)+str(likemodel)+self.doModelMapFlag['srcmap']+'.fits'
		self.childConfig['doModelMap']['srcmdl'] = modelDir+'out_'+self.childConfig['doLike']['srcmdl'].split('/')[-1] if self.doModelMapFlag['srcmdl'] == True else self.doModelMapFlag['srcmdl']
		self.childConfig['doModelMap']['outfile'] = defaultStem+'_'+str(interIncrement)+str(likemodel)+'_model.fits' if self.doModelMapFlag['outfile'] == True else defaultStem+'_'+str(interIncrement)+str(likemodel)+self.doModelMapFlag['outfile']+'.fits'
		self.childConfig['doModelMap']['expcube'] = defaultStem+'_'+str(interIncrement)+'_livetime.fits' if self.doModelMapFlag['expcube'] == True else defaultStem+'_'+str(interIncrement)+self.doModelMapFlag['expcube']+'.fits'
		self.childConfig['doModelMap']['bexpmap'] = defaultStem+'_'+str(interIncrement)+'_exposure.fits' if self.doModelMapFlag['bexpmap'] == True else defaultStem+'_'+str(interIncrement)+self.doModelMapFlag['bexpmap']+'.fits'

		self.childConfig['doResidual']['infile1'] = self.general['saveNameStem']+'_'+str(interIncrement)+'_cmap.fits' if self.doResidualFlag['infile1'] == True else self.general['saveNameStem']+'_'+str(interIncrement)+self.doResidualFlag['infile1']+'.fits'
		self.childConfig['doResidual']['infile2'] = self.general['saveNameStem']+'_'+str(interIncrement)+str(likemodel)+'_model.fits' if self.doResidualFlag['infile2'] == True else self.general['saveNameStem']+'_'+str(interIncrement)+str(likemodel)+self.doResidualFlag['infile2']+'.fits'
		self.childConfig['doResidual']['outfile'] = self.general['saveNameStem']+'_'+str(interIncrement)+str(likemodel)+'_residual.fits' if self.doResidualFlag['outfile'] == True else self.general['saveNameStem']+'_'+str(interIncrement)+str(likemodel)+self.doResidualFlag['outfile']+'.fits'

	def unsetDefaults(self):

		self.childConfig['doFilter']['infile'] = 'NOPASS' if self.doFilterFlag['infile'] == True else self.doFilterFlag['infile']
		self.childConfig['doFilter']['outfile'] = 'NOPASS' if self.doFilterFlag['outfile'] == True else self.doFilterFlag['outfile']

		self.childConfig['doMaketime']['scfile'] = 'NOPASS' if self.doMaketimeFlag['scfile'] == True else self.doMaketimeFlag['scfile']
		self.childConfig['doMaketime']['evfile'] = 'NOPASS' if self.doMaketimeFlag['evfile'] == True else self.doMaketimeFlag['evfile']
		self.childConfig['doMaketime']['outfile'] = 'NOPASS' if self.doMaketimeFlag['outfile'] == True else self.doMaketimeFlag['outfile']
		
		self.childConfig['doModel']['infile'] = 'NOPASS' if self.doModelFlag['infile'] == True else self.doModelFlag['infile']
		self.childConfig['doModel']['outfile'] = 'NOPASS' if self.doModelFlag['outfile'] == True else self.doModelFlag['outfile']
		self.childConfig['doModel']['wd'] = 'NOPASS' if self.doModelFlag['wd'] == True else self.doModelFlag['wd']
		
		self.childConfig['doTempo']['infile'] = 'NOPASS' if self.doTempoFlag['infile'] == True else self.doTempoFlag['infile']
		self.childConfig['doTempo']['scfile'] = 'NOPASS' if self.doTempoFlag['scfile'] == True else self.doTempoFlag['scfile']
		self.childConfig['doTempo']['outfile'] = 'NOPASS' if self.doTempoFlag['outfile'] == True else self.doTempoFlag['outfile']
		
		self.childConfig['doFold']['infile'] = 'NOPASS' if self.doFoldFlag['infile'] == True else self.doFoldFlag['infile']
		self.childConfig['doFold']['outfile'] = 'NOPASS' if self.doFoldFlag['outfile'] == True else self.doFoldFlag['outfile']
		
		self.childConfig['doSort']['infile'] = 'NOPASS' if self.doSortFlag['infile'] == True else self.doSortFlag['infile']
		self.childConfig['doSort']['scfile'] = 'NOPASS' if self.doSortFlag['scfile'] == True else self.doSortFlag['scfile']
		self.childConfig['doSort']['outfile'] = 'NOPASS' if self.doSortFlag['outfile'] == True else self.doSortFlag['outfile']
		
		self.childConfig['doCmap']['evfile'] = 'NOPASS' if self.doCmapFlag['evfile'] == True else self.doCmapFlag['evfile']
		self.childConfig['doCmap']['scfile'] = 'NOPASS' if self.doCmapFlag['scfile'] == True else self.doCmapFlag['scfile']
		self.childConfig['doCmap']['outfile'] = 'NOPASS' if self.doCmapFlag['outfile'] == True else self.doCmapFlag['outfile']		
		
		self.childConfig['doCCUBE']['evfile'] = 'NOPASS' if self.doCCUBEFlag['evfile'] == True else self.doCCUBEFlag['evfile']
		self.childConfig['doCCUBE']['scfile'] = 'NOPASS' if self.doCCUBEFlag['scfile'] == True else self.doCCUBEFlag['scfile']
		self.childConfig['doCCUBE']['outfile'] = 'NOPASS' if self.doCCUBEFlag['outfile'] == True else self.doCCUBEFlag['outfile']
		
		self.childConfig['doLivetime']['evfile'] = 'NOPASS' if self.doLivetimeFlag['evfile'] == True else self.doLivetimeFlag['evfile']
		self.childConfig['doLivetime']['scfile'] = 'NOPASS' if self.doLivetimeFlag['scfile'] == True else self.doLivetimeFlag['outfile']
		self.childConfig['doLivetime']['outfile'] = 'NOPASS' if self.doLivetimeFlag['outfile'] == True else self.doLivetimeFlag['outfile']
		
		self.childConfig['doExposure']['infile'] = 'NOPASS' if self.doExposureFlag['infile'] == True else self.doExposureFlag['infile']
		self.childConfig['doExposure']['cmap'] = 'NOPASS' if self.doExposureFlag['cmap'] == True else self.doExposureFlag['cmap']
		self.childConfig['doExposure']['outfile'] = 'NOPASS' if self.doExposureFlag['outfile'] == True else self.doExposureFlag['outfile']
		
		self.childConfig['doSrc']['scfile'] = 'NOPASS' if self.doSrcFlag['scfile'] == True else self.doSrcFlag['scfile']
		self.childConfig['doSrc']['expcube'] = 'NOPASS' if self.doSrcFlag['expcube'] == True else self.doSrcFlag['expcube']
		self.childConfig['doSrc']['cmap'] = 'NOPASS' if self.doSrcFlag['cmap'] == True else self.doSrcFlag['cmap']
		self.childConfig['doSrc']['srcmdl'] = 'NOPASS' if self.doSrcFlag['srcmdl'] == True else self.doSrcFlag['srcmdl']
		self.childConfig['doSrc']['bexpmap'] = 'NOPASS' if self.doSrcFlag['bexpmap'] == True else self.doSrcFlag['bexpmap']
		self.childConfig['doSrc']['outfile'] = 'NOPASS' if self.doSrcFlag['outfile'] == True else self.doSrcFlag['outfile']

		self.childConfig['doLike']['srcmap'] = 'NOPASS' if self.doLikeFlag['srcmap'] == True else self.doLikeFlag['srcmap']		
		self.childConfig['doLike']['expcube'] = 'NOPASS' if self.doLikeFlag['expcube'] == True else self.doLikeFlag['expcube']		
		self.childConfig['doLike']['bexpmap'] = 'NOPASS' if self.doLikeFlag['bexpmap'] == True else self.doLikeFlag['bexpmap']
		self.childConfig['doLike']['srcmdl'] = 'NOPASS' if self.doLikeFlag['srcmdl'] == True else self.doLikeFlag['srcmdl']
		self.childConfig['doLike']['outmodel'] = 'NOPASS' if self.doLikeFlag['outmodel'] == True else self.doLikeFlag['outmodel']
		self.childConfig['doLike']['results'] = 'NOPASS' if self.doLikeFlag['results'] == True else self.doLikeFlag['results']
		self.childConfig['doLike']['specfile'] = 'NOPASS' if self.doLikeFlag['specfile'] == True else self.doLikeFlag['specfile']
		self.childConfig['doLike']['emin'] = 'NOPASS' if self.doLikeFlag['emin'] == True else self.doLikeFlag['emin']
		self.childConfig['doLike']['emax'] = 'NOPASS' if self.doLikeFlag['emax'] == True else self.doLikeFlag['emax']
		
		self.childConfig['doModelMap']['srcmaps'] = 'NOPASS' if self.doModelMapFlag['srcmaps'] == True else self.doModelMapFlag['srcmaps']
		self.childConfig['doModelMap']['srcmdl'] = 'NOPASS' if self.doModelMapFlag['srcmdl'] == True else self.doModelMapFlag['srcmdl']
		self.childConfig['doModelMap']['outfile'] = 'NOPASS' if self.doModelMapFlag['outfile'] == True else self.doModelMapFlag['outfile']
		self.childConfig['doModelMap']['expcube'] = 'NOPASS' if self.doModelMapFlag['expcube'] == True else self.doModelMapFlag['expcube']
		self.childConfig['doModelMap']['bexpmap'] = 'NOPASS' if self.doModelMapFlag['bexpmap'] == True else self.doModelMapFlag['bexpmap']

		self.childConfig['doResidual']['infile1'] = 'NOPASS' if self.doResidualFlag['infile1'] == True else self.doResidualFlag['infile1']
		self.childConfig['doResidual']['infile2'] = 'NOPASS' if self.doResidualFlag['infile2'] == True else self.doResidualFlag['infile2']
		self.childConfig['doResidual']['outfile'] = 'NOPASS' if self.doResidualFlag['outfile'] == True else self.doResidualFlag['outfile']


class ecumenical():
	
	"""This object's primary purpose is to be a container for runlistMember objects."""
	
	def __init__(self, root_python_program = None, masterConfigFilename = None, c = None):
		
		"""Given a path to the master config file, Pretty much everything useful is done at instantiation."""
		
		self.root_python_program = root_python_program if root_python_program is not None else '##DEFAULT##'
		self.masterConfigFilename = masterConfigFilename if masterConfigFilename is not None else sys.exit('Error. No master Configuration file!')
		self.c = c if c is not None else GFF.colors()
	
		self.masterConfig = ConfigParser(interpolation=ExtendedInterpolation(),inline_comment_prefixes=('#'))
		self.masterConfig.optionxform = str
		self.masterConfig.read(masterConfigFilename)
		
		print('Loading in the master configuration file...')
		
		self.general = od(self.masterConfig['General'])
		self.sections = od(self.masterConfig['Sections'])

		for key in self.general:
			self.general[key] = GFF.tryeval(self.general[key])		
		for selection in self.sections:
			self.sections[selection] = GFF.tryeval(self.sections[selection])		
		
		if self.general['ansiColors'] == True:
			self.c.enableColors()
			self.c.confirmColorsDonger()

		self.members = od({})
		for selection in self.sections:
			if self.sections[selection] == True:
				self.members[selection] = fermiRunlistMember(self.masterConfig, selection, self.c)
				
	def __getitem__(self, key):
		return self.members[key]

	def to_list(self):
		return list(self.members.values())