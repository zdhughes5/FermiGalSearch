#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 15:27:51 2017

@author: zdhughes
"""

import general_functions_fermi as GFF
import analysisClean as ac
test = ac.fermiCondorWrapper()
test.setupClassVariables('masterClean.conf')


test.ecumenical['Main'].printInfo()




	def run(self, masterConfigFileName):
		
		self.setupClassVariables(masterConfigFileName)
		
		if self.generalSection['runFlags']['main'] == True:
			self.loopSection(self.runMainSection, self.mainConfig)
		if self.generalSection['runFlags']['months'] == True:
			self.loopSection(self.runMonthsSection, self.monthsConfig)
			
			
				#This loops over the on sections in the master (main, etc.) and creates condor entries for the on processes
	def loopSection(self, ecuMember):
		
		for i, key in enumerate(masterSection):
			if masterSection[key]:
				if not (key == 'doTempo' or key == 'doFold' or key == 'doLike'):
					print(self.c.green(key)+' set to '+self.c.blue(masterSection[key])+'. Running section...')
					self.buildFermiCondorJob(childConfig, key)
				elif key == 'doTempo':
					print(self.c.green(key)+' set to '+self.c.blue(masterSection[key])+'. Running section...')
					self.pulsarization(childConfig, key)

				elif key == 'doFold':
					print(self.c.green(key)+' set to '+self.c.blue(masterSection[key])+'. Running section...')
					self.binarification(childConfig, key)
				elif key == 'doLike':
					print(self.c.green(key)+' set to '+self.c.blue(masterSection[key])+'. Running section...')
					self.standardLiklihood(childConfig, key)
			elif not masterSection[key]:
				print(self.c.green(key)+' set to '+self.c.lightred(masterSection[key])+'. Skipping section...')
	
	#This builds the on sections.
	def buildFermiCondorJob(self, childConfig, sectionName, topSection = None):	

		if topSection == 'Main':
			job, executable, stage, textDir = GFF.getCondorParameters(self.generalSection['mainDir'], topSection)
		sectionOut,  = GFF.nopassSet(childConfig, sectionName, self.generalSection)	

		print('Creating directory '+self.c.yellow(textDir)+' for logs.')
		subprocess.call('mkdir -p '+textDir, shell=True)
		
		print('Constructing condor job for '+self.c.green(executable.split('/')[-1])+' to be executed in directory '+self.c.yellow(self.generalSection['mainDir']))
		
		GFF.makeCondorHeader(job, executable, self.root_python_program, stage, sectionName, self.c)
		arguments = GFF.setCommandlineArgs(sectionOut)
		condorEntries = {
			'output' : textDir+'/'+'src_'+self.generalSection['saveName']+'.out\n',
			'error' : textDir+'/'+'src_'+self.generalSection['saveName']+'.err\n',
			'log' : textDir+'/'+'src_'+self.generalSection['saveName']+'.log\n',
			'requirements' : '(machine == "herc0") || (machine == "herc2") || (machine == "starscream.lexas")\n',
			'arguments' : arguments+'\n'
			}
		GFF.makeCondorBody(job, condorEntries, self.c)

	def pulsarization(self, childConfig, sectionName, quiet = None):

		
		section =  dict(childConfig.items(sectionName))
		section = GFF.convertSectionTypes(section)
		
		sectionOut, job, executable, stage, textDir = GFF.nopassSet(section, sectionName, self.generalSection)	
		if not quiet:
			print('Constructing condor job for '+self.c.green(executable.split('/')[-1])+' to be executed in directory '+self.c.yellow(self.generalSection['mainDir']))
		
		cwd = os.getcwd()
		os.chdir(self.generalSection['mainDir'])
		tempo = 'tempo2 -gr fermi -ft1 '+sectionOut['infile']+' -ft2 '+sectionOut['scfile']+' -f '+sectionOut['ephemeris']+' -phase -graph 0'
		print('Calling: \n'+self.c.purple(tempo))
		subprocess.call(tempo, shell=True)
		pulsarCut = 'ftselect '+sectionOut['infile']+'[events] '+sectionOut['outfile']+' "(PULSE_PHASE > 0.23 && PULSE_PHASE < 0.53) || (PULSE_PHASE > 0.65 && PULSE_PHASE < 0.99)"'
		subprocess.call(pulsarCut, shell=True)
		os.chdir(cwd)

				
	def binarification(self, childConfig, sectionName, quiet = None):
		
		section =  dict(childConfig.items(sectionName))
		section = GFF.convertSectionTypes(section)
		
		sectionOut, job, executable, stage, textDir = GFF.nopassSet(section, sectionName, self.generalSection)	
		if not quiet:
			print('Constructing condor job for '+self.c.green(executable.split('/')[-1])+' to be executed in directory '+self.c.yellow(self.generalSection['mainDir']))
		
		
		cwd = os.getcwd()
		os.chdir(self.generalSection['mainDir'])		
		subprocess.call('cp '+sectionOut['infile']+' '+self.generalSection['saveName']+'_intermediate.fits',shell=True)
		subprocess.call('fcalc '+self.generalSection['saveName']+'_intermediate.fits[1] '+self.generalSection['saveName']+'_offset.fits offset "time - 254620800"',shell=True)
		subprocess.call("fcalc "+self.generalSection['saveName']+"_offset.fits[1] "+self.generalSection['saveName']+"_intermediate_2.fits intermediate '(((offset > 0*27216000) && (offset < 1*27216000))?((offset-0*27216000)/27216000):(((offset > 1*27216000) && (offset < 2*27216000))?((offset-1*27216000)/27216000):(((offset > 2*27216000) && (offset < 3*27216000))?((offset-2*27216000)/27216000):(((offset > 3*27216000) && (offset < 4*27216000))?((offset-3*27216000)/27216000):(((offset > 4*27216000) && (offset < 5*27216000))?((offset-4*27216000)/27216000):(((offset > 5*27216000) && (offset < 6*27216000))?((offset-5*27216000)/27216000):(((offset > 6*27216000) && (offset < 7*27216000))?((offset-6*27216000)/27216000):(((offset < 0*27216000))?((offset)/27216000+1):(offset)))))))))'",shell=True)
		subprocess.call("fcalc "+self.generalSection['saveName']+"_intermediate_2.fits[1] "+sectionOut['outfile']+" binary '(((intermediate > 7*27216000) && (intermediate < 8*27216000))?((intermediate-7*27216000)/27216000):(((intermediate > 8*27216000) && (intermediate < 9*27216000))?((intermediate-8*27216000)/27216000):(((intermediate > 9*27216000) && (intermediate < 10*27216000))?((intermediate-9*27216000)/27216000):(((intermediate > 10*27216000) && (intermediate < 11*27216000))?((intermediate-10*27216000)/27216000):(((intermediate > 11*27216000) && (intermediate < 12*27216000))?((intermediate-11*27216000)/27216000):(((intermediate > 12*27216000) && (intermediate < 13*27216000))?((intermediate-12*27216000)/27216000):(((intermediate > 13*27216000) && (intermediate < 14*27216000))?((intermediate-13*27216000)/27216000):(intermediate))))))))'",shell=True)
		subprocess.call('rm '+self.generalSection['saveName']+'_intermediate.fits '+self.generalSection['saveName']+'_intermediate_2.fits '+self.generalSection['saveName']+'_offset.fits' ,shell=True)
		os.chdir(cwd)
		
	def standardLiklihood(self, childConfig, sectionName, quiet = None):
		
		pythonProgram = '/home/zdhughes/Desktop/projects/FermiGalSearch/please_gtlike.py'
		section =  dict(childConfig.items(sectionName))
		section = GFF.convertSectionTypes(section)
		
		sectionOut, job, executable, stage, textDir = GFF.nopassSet(section, sectionName, self.generalSection)	
		if not quiet:
			print('Constructing condor job for '+self.c.green(executable.split('/')[-1])+' to be executed in directory '+self.c.yellow(self.generalSection['mainDir']))
		
		if not quiet:
			print('Creating directory '+self.c.yellow(textDir)+' for logs.')
		subprocess.call('mkdir -p '+textDir, shell=True)
		
		if not quiet:
			print('Constructing condor job for '+self.c.green(executable.split('/')[-1])+' to be executed in directory '+self.c.yellow(self.generalSection['mainDir']))
		
		GFF.makeCondorHeader(job, executable, self.root_python_program, stage, sectionName, self.c)
		arguments = GFF.setCommandlineArgs(sectionOut)
		
		modelIn = [x for x in arguments.split() if x.split('=')[0] == 'model'][0]
		srcmapIn = [x for x in arguments.split() if x.split('=')[0] == 'srcmap'][0]
		livetimeIn = [x for x in arguments.split() if x.split('=')[0] == 'livetime'][0]
		expmapIn = [x for x in arguments.split() if x.split('=')[0] == 'expmap'][0]
		outmodelIn = [x for x in arguments.split() if x.split('=')[0] == 'outmodel'][0]
		
		arguments = ' '.join([pythonProgram, self.generalSection['mainDir'], modelIn, srcmapIn, livetimeIn, expmapIn, outmodelIn])
		
		condorEntries = {
			'output' : textDir+'/'+'src_'+self.generalSection['saveName']+'.out\n',
			'error' : textDir+'/'+'src_'+self.generalSection['saveName']+'.err\n',
			'log' : textDir+'/'+'src_'+self.generalSection['saveName']+'.log\n',
			'requirements' : '(machine == "herc0") || (machine == "herc2") || (machine == "starscream.lexas")\n',
			'arguments' : arguments+'\n'
			}
		GFF.makeCondorBody(job, condorEntries, self.c)
		
#test = fermiCondorWrapper('python35')
#test.setupClassVariables('masterClean.conf')
#test.loopSection()

#code.interact(local=locals())
#sys.exit('Code Break!')

def nopassSet(childConfig, sectionName, directory, saveName, generalSection, inter='main'):

	section =  convertSectionTypes(dict(childConfig.items(sectionName)))

	defaultStem = directory+saveName

	if sectionName == 'doFilter':
		section['infile'] = generalSection['runlistLoc']
		section['outfile'] = defaultStem+'_'+str(inter)+'_filter.fits'

	if sectionName == 'doMaketime':
		section['scfile'] = generalSection['scLoc']
		section['evfile'] = defaultStem+'_'+str(inter)+'_filter.fits'
		section['outfile'] = defaultStem+'_'+str(inter)+'_gti.fits'

	if sectionName == 'doTempo':
		section['infile'] = defaultStem+'_'+str(inter)+'_gti.fits'
		section['scfile'] = generalSection['scLoc']
		section['outfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'

	if sectionName == 'doFold':
		section['infile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
		section['outfile'] = defaultStem+'_'+str(inter)+'_binary.fits'

	if sectionName == 'doCCUBE':
		section['evfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
		section['scfile'] = generalSection['scLoc']
		section['outfile'] = 'none'

	if sectionName == 'doLivetime':
		section['evfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
		section['scfile'] = generalSection['scLoc']
		section['outfile'] = defaultStem+'_'+str(inter)+'_livetime.fits'

	if sectionName == 'doExposure':
		section['infile'] = defaultStem+'_'+str(inter)+'_livetime.fits'
		section['cmap'] = defaultStem+'_'+str(inter)+'_ccube.fits'
		section['outfile'] = defaultStem+'_'+str(inter)+'_exposure.fits'
        
	if sectionName == 'doSrc':
		section['scfile'] = generalSection['scLoc']
		section['expcube'] = defaultStem+'_'+str(inter)+'_livetime.fits'
		section['cmap'] = defaultStem+'_'+str(inter)+'_ccube.fits'
		section['bexpmap'] = defaultStem+'_'+str(inter)+'_exposure.fits'
		section['outfile'] = defaultStem+'_'+str(inter)+'_srcmap.fits'

	if sectionName == 'doLike':
		section['srcmap'] = defaultStem+'_'+str(inter)+'_srcmap.fits'
		section['livetime'] = defaultStem+'_'+str(inter)+'_livetime.fits'
		section['expmap'] = defaultStem+'_'+str(inter)+'_exposure.fits'
		section['outmodel'] = directory+'out_'+section['model'].split('/')[-1]

	if sectionName == 'doSort':
		section['infile'] = defaultStem+'_'+str(inter)+'_gti.fits'
		section['scfile'] = generalSection['scLoc']
		section['outfile'] = defaultStem+'_'+str(inter)+'_gti_phasecuts.fits'

	return section
	
def nopassSet2(ecuMemberObj, generalSection, inter='main'):

	directory = ecuMemberObj.topConfig['directory']
	defaultStem = directory+generalSection['saveName']

	for section in ecuMemberObj.childConfig:
		if section != 'DEFAULT':

			if section == 'doFilter':
				ecuMemberObj.childConfig[section]['infile'] = generalSection['runlistFile']
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_filter.fits'

			if section == 'doMaketime':
				ecuMemberObj.childConfig[section]['scfile'] = generalSection['spacecraftFile']
				ecuMemberObj.childConfig[section]['evfile'] = defaultStem+'_'+str(inter)+'_filter.fits'
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_gti.fits'

			if section == 'doTempo':
				ecuMemberObj.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_gti.fits'
				ecuMemberObj.childConfig[section]['scfile'] = generalSection['spacecraftFile']
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'

			if section == 'doFold':
				ecuMemberObj.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_binary.fits'

			if section == 'doCCUBE':
				ecuMemberObj.childConfig[section]['evfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
				ecuMemberObj.childConfig[section]['scfile'] = generalSection['spacecraftFile']
				ecuMemberObj.childConfig[section]['outfile'] = 'none'

			if section == 'doLivetime':
				ecuMemberObj.childConfig[section]['evfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
				ecuMemberObj.childConfig[section]['scfile'] = generalSection['spacecraftFile']
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_livetime.fits'

			if section == 'doExposure':
				ecuMemberObj.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_livetime.fits'
				ecuMemberObj.childConfig[section]['cmap'] = defaultStem+'_'+str(inter)+'_ccube.fits'
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_exposure.fits'

			if section == 'doSrc':
				ecuMemberObj.childConfig[section]['scfile'] = generalSection['spacecraftFile']
				ecuMemberObj.childConfig[section]['expcube'] = defaultStem+'_'+str(inter)+'_livetime.fits'
				ecuMemberObj.childConfig[section]['cmap'] = defaultStem+'_'+str(inter)+'_ccube.fits'
				ecuMemberObj.childConfig[section]['bexpmap'] = defaultStem+'_'+str(inter)+'_exposure.fits'
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_srcmap.fits'

			if section == 'doLike':
				ecuMemberObj.childConfig[section]['srcmap'] = defaultStem+'_'+str(inter)+'_srcmap.fits'
				ecuMemberObj.childConfig[section]['livetime'] = defaultStem+'_'+str(inter)+'_livetime.fits'
				ecuMemberObj.childConfig[section]['expmap'] = defaultStem+'_'+str(inter)+'_exposure.fits'
				ecuMemberObj.childConfig[section]['outmodel'] = directory+'out_'+ecuMemberObj.childConfig[section]['model'].split('/')[-1]

			if section == 'doSort':
				ecuMemberObj.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_gti.fits'
				ecuMemberObj.childConfig[section]['scfile'] = generalSection['spacecraftFile']
				ecuMemberObj.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_gti_phasecuts.fits'

	return ecuMemberObj




	def setDefaults(self, inter = 'main'):

		directory = self.topConfig['directory']
		defaultStem = directory+self.generalSection['saveNameStem']

		for section in self.childConfig:
			if section != 'DEFAULT':

				if section == 'doFilter':
					self.childConfig[section]['infile'] = self.generalSection['runlistFile']
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_filter.fits'

				if section == 'doMaketime':
					self.childConfig[section]['scfile'] = self.generalSection['spacecraftFile']
					self.childConfig[section]['evfile'] = defaultStem+'_'+str(inter)+'_filter.fits'
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_gti.fits'

				if section == 'doTempo':
					self.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_gti.fits'
					self.childConfig[section]['scfile'] = self.generalSection['spacecraftFile']
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'

				if section == 'doFold':
					self.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_binary.fits'

				if section == 'doCCUBE':
					self.childConfig[section]['evfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
					self.childConfig[section]['scfile'] = self.generalSection['spacecraftFile']
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_ccube.fits'

				if section == 'doLivetime':
					self.childConfig[section]['evfile'] = defaultStem+'_'+str(inter)+'_phasecuts.fits'
					self.childConfig[section]['scfile'] = self.generalSection['spacecraftFile']
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_livetime.fits'

				if section == 'doExposure':
					self.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_livetime.fits'
					self.childConfig[section]['cmap'] = defaultStem+'_'+str(inter)+'_ccube.fits'
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_exposure.fits'

				if section == 'doSrc':
					self.childConfig[section]['scfile'] = self.generalSection['spacecraftFile']
					self.childConfig[section]['expcube'] = defaultStem+'_'+str(inter)+'_livetime.fits'
					self.childConfig[section]['cmap'] = defaultStem+'_'+str(inter)+'_ccube.fits'
					self.childConfig[section]['bexpmap'] = defaultStem+'_'+str(inter)+'_exposure.fits'
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_srcmap.fits'

				if section == 'doLike':
					self.childConfig[section]['srcmap'] = defaultStem+'_'+str(inter)+'_srcmap.fits'
					self.childConfig[section]['livetime'] = defaultStem+'_'+str(inter)+'_livetime.fits'
					self.childConfig[section]['expmap'] = defaultStem+'_'+str(inter)+'_exposure.fits'
					self.childConfig[section]['outmodel'] = directory+'out_'+self.childConfig[section]['model'].split('/')[-1]

				if section == 'doSort':
					self.childConfig[section]['infile'] = defaultStem+'_'+str(inter)+'_gti.fits'
					self.childConfig[section]['scfile'] = self.generalSection['spacecraftFile']
					self.childConfig[section]['outfile'] = defaultStem+'_'+str(inter)+'_gti_phasecuts.fits'
					
					
###PYTHON LIKE STUFF

	if sectionName == 'doLike':
		job = directory+'condor_likeJob'
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/python'
		textDir = directory+'likeText'
		entries = {
			'output' : textDir+'/like_'+saveName+'.out',
			'log' : textDir+'/like_'+saveName+'.log',
			'error' : textDir+'/like_'+saveName+'.err'
			}

		self.doLikeFlag = {'model':False, 'srcmap':False, 'livetime':False, 'expmap':False, 'outmodel':False}
		
		
		self.doLikeFlag['model'] = True if self.childConfig['doLike']['model'] == 'NOPASS' else self.childConfig['doLike']['model']		
		self.doLikeFlag['srcmap'] = True if self.childConfig['doLike']['srcmap'] == 'NOPASS' else self.childConfig['doLike']['srcmap']
		self.doLikeFlag['livetime'] = True if self.childConfig['doLike']['livetime'] == 'NOPASS' else self.childConfig['doLike']['livetime']
		self.doLikeFlag['expmap'] = True if self.childConfig['doLike']['expmap'] == 'NOPASS' else self.childConfig['doLike']['expmap']
		self.doLikeFlag['outmodel'] = True if self.childConfig['doLike']['outmodel'] == 'NOPASS' else self.childConfig['doLike']['outmodel']
		
		
		
		self.childConfig['doLike']['model'] = modelStem+'_'+str(inter)+'_model.xml' if self.doLikeFlag['model'] == True else self.doLikeFlag['model']
		self.childConfig['doLike']['srcmap'] = defaultStem+'_'+str(inter)+'_srcmap.fits' if self.doLikeFlag['srcmap'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['srcmap']+'.fits'
		self.childConfig['doLike']['livetime'] = defaultStem+'_'+str(inter)+'_livetime.fits' if self.doLikeFlag['livetime'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['livetime']+'.fits'
		self.childConfig['doLike']['expmap'] = defaultStem+'_'+str(inter)+'_exposure.fits' if self.doLikeFlag['expmap'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['expmap']+'.fits'
		self.childConfig['doLike']['outmodel'] = modelDir+'out_'+self.childConfig['doLike']['model'].split('/')[-1] if self.doLikeFlag['outmodel'] == True else self.doLikeFlag['outmodel']
		
		self.childConfig['doLike']['model'] = 'NOPASS' if self.doLikeFlag['model'] == True else self.doLikeFlag['model']		
		self.childConfig['doLike']['srcmap'] = 'NOPASS' if self.doLikeFlag['srcmap'] == True else self.doLikeFlag['srcmap']
		self.childConfig['doLike']['livetime'] = 'NOPASS' if self.doLikeFlag['livetime'] == True else self.doLikeFlag['livetime']
		self.childConfig['doLike']['expmap'] = 'NOPASS' if self.doLikeFlag['expmap'] == True else self.doLikeFlag['expmap']
		self.childConfig['doLike']['outmodel'] = 'NOPASS' if self.doLikeFlag['outmodel'] == True else self.doLikeFlag['outmodel']
[doLike]
model = NOPASS
srcmap = NOPASS
livetime = NOPASS
expmap = NOPASS
outmodel = NOPASS		
		
		
		
		
			self.doLikeFlag = {'expcube':False, 'srcmdl':False, 'sfile':False, 'results':False, 'specfile':False, 'evfile':False, 'scfile':False, 'cmap':False, 'bexpmap':False}
		self.doLikeFlag['expcube'] = True if self.childConfig['doLike']['expcube'] == 'NOPASS' else self.childConfig['doLike']['expcube']		
		self.doLikeFlag['srcmdl'] = True if self.childConfig['doLike']['srcmdl'] == 'NOPASS' else self.childConfig['doLike']['srcmdl']
		self.doLikeFlag['sfile'] = True if self.childConfig['doLike']['sfile'] == 'NOPASS' else self.childConfig['doLike']['sfile']
		self.doLikeFlag['results'] = True if self.childConfig['doLike']['results'] == 'NOPASS' else self.childConfig['doLike']['results']
		self.doLikeFlag['specfile'] = True if self.childConfig['doLike']['specfile'] == 'NOPASS' else self.childConfig['doLike']['specfile']
		self.doLikeFlag['evfile'] = True if self.childConfig['doLike']['evfile'] == 'NOPASS' else self.childConfig['doLike']['evfile']		
		self.doLikeFlag['scfile'] = True if self.childConfig['doLike']['scfile'] == 'NOPASS' else self.childConfig['doLike']['scfile']
		self.doLikeFlag['cmap'] = True if self.childConfig['doLike']['cmap'] == 'NOPASS' else self.childConfig['doLike']['cmap']
		self.doLikeFlag['bexpmap'] = True if self.childConfig['doLike']['bexpmap'] == 'NOPASS' else self.childConfig['doLike']['bexpmap']
		self.childConfig['doLike']['expcube'] = defaultStem+'_'+str(inter)+'_livetime.fits' if self.doLikeFlag['expcube'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['expcube']+'.fits'
		self.childConfig['doLike']['srcmdl'] = modelStem+'_'+str(inter)+'_model.xml' if self.doLikeFlag['srcmdl'] == True else self.doLikeFlag['srcmap']
		self.childConfig['doLike']['sfile'] = modelDir+'out_'+self.childConfig['doLike']['srcmdl'].split('/')[-1] if self.doLikeFlag['sfile'] == True else self.doLikeFlag['sfile']
		self.childConfig['doLike']['results'] = defaultStem+'_'+str(inter)+'_results.dat' if self.doLikeFlag['results'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['results']+'.dat'
		self.childConfig['doLike']['specfile'] = defaultStem+'_'+str(inter)+'_spec.fits' if self.doLikeFlag['specfile'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['specfile']+'.fits'
		self.childConfig['doLike']['evfile'] = defaultStem+'_'+str(inter)+'_srcmap.fits' if self.doLikeFlag['evfile'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['evfile']+'.fits'
		self.childConfig['doLike']['cmap'] = defaultStem+'_'+str(inter)+'_ccube.fits' if self.doLikeFlag['cmap'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['cmap']+'.fits'
		self.childConfig['doLike']['bexpmap'] = defaultStem+'_'+str(inter)+'_exposure.fits' if self.doLikeFlag['bexpmap'] == True else defaultStem+'_'+str(inter)+self.doLikeFlag['bexpmap']+'.fits'
			self.childConfig['doLike']['expcube'] = 'NOPASS' if self.doLikeFlag['expcube'] == True else self.doLikeFlag['expcube']		
		self.childConfig['doLike']['srcmdl'] = 'NOPASS' if self.doLikeFlag['srcmdl'] == True else self.doLikeFlag['srcmdl']
		self.childConfig['doLike']['sfile'] = 'NOPASS' if self.doLikeFlag['sfile'] == True else self.doLikeFlag['sfile']
		self.childConfig['doLike']['results'] = 'NOPASS' if self.doLikeFlag['results'] == True else self.doLikeFlag['results']
		self.childConfig['doLike']['specfile'] = 'NOPASS' if self.doLikeFlag['specfile'] == True else self.doLikeFlag['specfile']
		self.childConfig['doLike']['evfile'] = 'NOPASS' if self.doLikeFlag['evfile'] == True else self.doLikeFlag['evfile']		
		self.childConfig['doLike']['scfile'] = 'NOPASS' if self.doLikeFlag['scfile'] == True else self.doLikeFlag['scfile']
		self.childConfig['doLike']['cmap'] = 'NOPASS' if self.doLikeFlag['cmap'] == True else self.doLikeFlag['cmap']
		self.childConfig['doLike']['bexpmap'] = 'NOPASS' if self.doLikeFlag['bexpmap'] == True else self.doLikeFlag['bexpmap']
	
		
		
		
		
		
		
		
		
		#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 15:21:17 2017

@author: zdhughes
"""

import configHandler as ch
import general_functions_fermi as GFF
import subprocess
import astropy

import sys
import code

def doStuff(member):
	

#Command line varibales
calling_program, masterConigFilename = sys.argv

#Create handler
handler = ch.ecumenical(calling_program, masterConigFilename)
c = handler.c

print(c.lightblue('\n+++++++++++ RUNNER +++++++++++\n\n'))
print('Creating working directory '+c.yellow(handler.generalSection['workingDir'])+'\n')
subprocess.call('mkdir -p '+handler.generalSection['workingDir'], shell=True)

for member in handler.members:
	#Loop over the unique sections and execute them.
	print('Working on section '+c.green(member)+'. Making directores...')
	print('Top section directory '+c.yellow(handler[member].getConfigOption('directory')))
	subprocess.call('mkdir -p '+handler[member].getConfigOption('directory'), shell=True)
	print('Model directory '+c.yellow(handler[member].getConfigOption('modelDir'))+'\n')
	subprocess.call('mkdir -p '+handler[member].getConfigOption('modelDir'), shell=True)	
	
	#Check if its Main, basically.
	if len(handler[member].range) == 1:
		
		handler[member].setDefaults()
		
		for doSection in handler[member].topSection:
			
			if handler[member].topSection.getboolean(doSection) == True:
				
				print('\n'+c.lightgreen(doSection)+' set to '+c.lightblue(handler[member].topSection[doSection])+' in section '+c.green(member))
				
				if handler.generalSection['verbosity'] == '2':
					handler[member].printSection(doSection)
				
				if doSection == 'doModel':
					GFF.runMake3FGL(**handler[member].childConfig['doModel'], c=handler.c)
					continue
				
				if doSection == 'doResidual':
					subprocess.call('farith '+handler[member].childConfig['doResidual']['infile1']+' '+handler[member].childConfig['doResidual']['infile2']+' '+handler[member].childConfig['doResidual']['outfile']+' SUB',shell=True)
					continue

				
				job, executable, textDir, entries = GFF.getCondorFermiParameters(handler[member].getConfigOption('directory'), doSection, handler[member].saveName)
				subprocess.call('mkdir '+textDir, shell=True)

				print('Using these parameters for the condor submit file:\n Job: '+c.yellow(job)+'\n executable: '+c.purple(executable)+'\n textDir: '+c.yellow(textDir)+'\n')
				
				entries['arguments'] = GFF.setCommandlineArgs(handler[member].getChildSection(doSection))
				entries['requirements'] = '(machine == "herc0")'
				
				condorJob = GFF.condorHandler(filename=job, executable=executable, title=calling_program, subtitle=executable.split('/')[-1], tertiary=handler[member].saveName, c=handler.c)
				condorJob.addEntry(entries)
				condorJob.close()
				

				if handler.generalSection.getboolean('run') == True:
					condorJob.run(prepend='ferminit && ')
				
			else:
				print(c.lightgreen(doSection)+' set to '+c.lightred(handler[member].topSection[doSection])+' in section '+c.green(member))





#code.interact(local=locals())
#sys.exit('Code Break!')		 

		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
