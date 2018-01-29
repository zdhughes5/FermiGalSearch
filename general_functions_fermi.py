# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 14:27:43 2016

@author: zdhughes
"""
from time import gmtime, strftime, sleep, time
import sys
import ast
import subprocess
import code
import os

def getCondorFermiParameters(directory, sectionName, saveName, likemodel='main'):
	
	"""Given a gttool section and location this function will return parameters central to creating a fermi condor script."""
	
	if sectionName == 'doFilter':
		job = directory+'condor_filterJob'
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtselect'
		textDir = directory+'filterText'
		entries = {
			'output' : textDir+'/filter_'+saveName+'.out',
			'log' : textDir+'/filter_'+saveName+'.log',
			'error' : textDir+'/filter_'+saveName+'.err'
			}

	if sectionName == 'doMaketime':
		job = directory+'condor_maketimeJob'
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtmktime'
		textDir = directory+'maketimeText'
		entries = {
			'output' : textDir+'/maketime_'+saveName+'.out',
			'log' : textDir+'/maketime_'+saveName+'.log',
			'error' : textDir+'/maketime_'+saveName+'.err'
			}

	if sectionName == 'doTempo':
		job = directory+'condor_tempoJob'
		executable = ''
		textDir = directory+'tempoText'
		entries = {
			'output' : textDir+'/tempo_'+saveName+'.out',
			'log' : textDir+'/tempo_'+saveName+'.log',
			'error' : textDir+'/tempo_'+saveName+'.err'
			}

	if sectionName == 'doFold':
		job = directory+'condor_foldJob'
		executable = ''
		textDir = directory+'foldText'
		entries = {
			'output' : textDir+'/fold_'+saveName+'.out',
			'log' : textDir+'/fold_'+saveName+'.log',
			'error' : textDir+'/fold_'+saveName+'.err'
			}
		
	if sectionName == 'doSort':
		job = directory+'condor_sortJob'
		executable = ''
		textDir = directory+'sortText'
		entries = {
			'output' : textDir+'/sort_'+saveName+'.out',
			'log' : textDir+'/sort_'+saveName+'.log',
			'error' : textDir+'/sort_'+saveName+'.err'
			}
		
	if sectionName == 'doCmap':
		job = directory+'condor_cmapJob'
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtbin'
		textDir = directory+'cmapText'
		entries = {
			'output' : textDir+'/cmap_'+saveName+'.out',
			'log' : textDir+'/cmap_'+saveName+'.log',
			'error' : textDir+'/cmap_'+saveName+'.err'
			}

	if sectionName == 'doCCUBE':
		job = directory+'condor_ccubeJob'
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtbin'
		textDir = directory+'ccubeText'
		entries = {
			'output' : textDir+'/ccube_'+saveName+'.out',
			'log' : textDir+'/ccube_'+saveName+'.log',
			'error' : textDir+'/ccube_'+saveName+'.err'
			}

	if sectionName == 'doLivetime':
		job = directory+'condor_livetimeJob'
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtltcube'
		textDir = directory+'livetimeText'
		entries = {
			'output' : textDir+'/livetime_'+saveName+'.out',
			'log' : textDir+'/livetime_'+saveName+'.log',
			'error' : textDir+'/livetime_'+saveName+'.err'
			}

	if sectionName == 'doExposure':
		job = directory+'condor_exposureJob'
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtexpcube2'
		textDir = directory+'exposureText'
		entries = {
			'output' : textDir+'/exposure_'+saveName+'.out',
			'log' : textDir+'/exposure_'+saveName+'.log',
			'error' : textDir+'/exposure_'+saveName+'.err'
			}

	if sectionName == 'doSrc':
		job = directory+'condor_sourceJob'+str(likemodel)
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtsrcmaps'
		textDir = directory+'sourceText'
		entries = {
			'output' : textDir+'/src_'+saveName+str(likemodel)+'.out',
			'log' : textDir+'/src_'+saveName+str(likemodel)+'.log',
			'error' : textDir+'/src_'+saveName+str(likemodel)+'.err'
			}

	if sectionName == 'doLike':
		job = directory+'condor_likeJob'+str(likemodel)
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/python'
		textDir = directory+'likeText'
		entries = {
			'output' : textDir+'/like_'+saveName+str(likemodel)+'.out',
			'log' : textDir+'/like_'+saveName+str(likemodel)+'.log',
			'error' : textDir+'/like_'+saveName+str(likemodel)+'.err'
			}
		
	if sectionName == 'doModelMap':
		job = directory+'condor_modelmapJob'+str(likemodel)
		executable = '/nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/bin/gtmodel'
		textDir = directory+'modelmapText'
		entries = {
			'output' : textDir+'/modelmap_'+str(likemodel)+saveName+'.out',
			'log' : textDir+'/modelmap_'+str(likemodel)+saveName+'.log',
			'error' : textDir+'/modelmap_'+str(likemodel)+saveName+'.err'
			}

	return job, executable, textDir, entries

class tee():
	
	"tee implemented in python"
	
	def __init__(self, fd1, fd2):
		self.fd1 = fd1
		self.fd2 = fd2
		
	def __del__(self):
		
		stdStreams = [0, 1, 2]
		fd1_no = self.fd1.fileno()
		fd2_no = self.fd2.fileno()
		
		if fd1_no not in stdStreams:
			self.fd1.close()
		if fd2_no not in stdStreams:
			self.fd2.close()
	
	def write(self, text):
		self.fd1.write(text)
		self.fd2.write(text)

	def flush(self):
		self.fd1.flush()
		self.fd2.flush()


class colors():
	
	"""This class will color console text output using ANSI codes."""

	RED = ''
	ORANGE = ''
	YELLOW = ''
	GREEN = ''
	BLUE = ''
	INDIGO = ''
	VIOLET = ''
	PINK = ''                                                                        
	BLACK = ''
	CYAN = ''
	PURPLE = ''
	BROWN = ''
	GRAY = ''
	DARKGRAY = ''
	LIGHTBLUE = ''
	LIGHTGREEN = ''
	LIGHTCYAN = ''
	LIGHTRED = ''
	LIGHTPURPLE = ''
	WHITE = ''
	BOLD = ''
	UNDERLINE = ''
	ENDC = ''
    
	def enableColors(self):

		self.RED = '\033[0;31m'
		self.ORANGE = '\033[38;5;166m'
		self.YELLOW = '\033[1;33m'
		self.GREEN = '\033[0;32m'
		self.BLUE = '\033[0;34m'
		self.INDIGO = '\033[38;5;53m'
		self.VIOLET = '\033[38;5;163m'
		self.PINK =  '\033[38;5;205m'
		self.BLACK = '\033[0;30m'
		self.CYAN = '\033[0;36m'
		self.PURPLE = '\033[0;35m'
		self.BROWN = '\033[0;33m'
		self.GRAY = '\033[0;37m'
		self.DARKGRAY = '\033[1;30m'
		self.LIGHTBLUE = '\033[1;34m'
		self.LIGHTGREEN = '\033[1;32m'
		self.LIGHTCYAN = '\033[1;36m'
		self.LIGHTRED = '\033[1;31m'
		self.LIGHTPURPLE = '\033[1;35m'
		self.WHITE = '\033[1;37m'
		self.BOLD = '\033[1m'
		self.UNDERLINE = '\033[4m'
		self.ENDC = '\033[0m'

        
	def disableColors(self):
        
		self.RED = ''        
		self.ORANGE = ''
		self.YELLOW = ''
		self.GREEN = ''
		self.BLUE = ''
		self.INDIGO = ''
		self.VIOLET = ''
		self.PINK = ''
		self.BLACK = ''
		self.CYAN = ''
		self.PURPLE = ''
		self.BROWN = ''
		self.GRAY = ''
		self.DARKGRAY = ''
		self.LIGHTBLUE = ''
		self.LIGHTGREEN = ''
		self.LIGHTCYAN = ''
		self.LIGHTRED = ''
		self.LIGHTPURPLE = ''
		self.WHITE = ''
		self.BOLD = ''
		self.UNDERLINE = ''
		self.ENDC = ''

	def getState(self):
		if self.ENDC:
			return True
		elif not self.ENDC:
			return False
		else:
			return -1

	def flipState(self):
		if self.getState():
			self.disableColors()
		elif not self.getState():
			self.enableColors()
		else:
			sys.exit("Can't flip ANSI state, exiting.")

	def confirmColors(self):
		if self.getState() == True:
			print('Colors are '+self.red('e')+self.orange('n')+self.yellow('a')+self.green('b')+self.blue('l')+self.indigo('e')+self.violet('d'))
		elif self.getState() == False:
			print('Colors are off!')
		elif self.getState() == -1:
			print('Error: Can\'t get color state.')

	def confirmColorsDonger(self):
		if self.getState() == True:
			print('Colors are '+self.pink('(ﾉ')+self.lightblue('◕')+self.pink('ヮ')+self.lightblue('◕')+self.pink('ﾉ')+self.red('☆')+self.orange('.')+self.yellow('*')+self.green(':')+self.blue('･ﾟ')+self.indigo('✧')+self.violet(' enabled!'))    
		elif self.getState() == False:
			print('Colors are off!')
		elif self.getState() == -1:
			print('Error: Can\'t get color state.')

	def orange(self, inString):
		inString = str(self.ORANGE+str(inString)+self.ENDC)
		return inString
	def indigo(self, inString):
		inString = str(self.INDIGO+str(inString)+self.ENDC)
		return inString
	def violet(self, inString):
		inString = str(self.VIOLET+str(inString)+self.ENDC)
		return inString
	def pink(self, inString):
		inString = str(self.PINK+str(inString)+self.ENDC)
		return inString
	def black(self, inString):
		inString = str(self.BLACK+str(inString)+self.ENDC)
		return inString
	def blue(self, inString):
		inString = str(self.BLUE+str(inString)+self.ENDC)
		return inString
	def green(self, inString):
		inString = str(self.GREEN+str(inString)+self.ENDC)
		return inString
	def cyan(self, inString):
		inString = str(self.CYAN+str(inString)+self.ENDC)
		return inString
	def red(self, inString):
		inString = str(self.RED+str(inString)+self.ENDC)
		return inString
	def purple(self, inString):
		inString = str(self.PURPLE+str(inString)+self.ENDC)
		return inString
	def brown(self, inString):
		inString = str(self.BROWN+str(inString)+self.ENDC)
		return inString
	def gray(self, inString):
		inString = str(self.GRAY+str(inString)+self.ENDC)
		return inString
	def darkgray(self, inString):
		inString = str(self.DARKGRAY+str(inString)+self.ENDC)
		return inString
	def lightblue(self, inString):
		inString = str(self.LIGHTBLUE+str(inString)+self.ENDC)
		return inString
	def lightgreen(self, inString):
		inString = str(self.LIGHTGREEN+str(inString)+self.ENDC)
		return inString
	def lightcyan(self, inString):
		inString = str(self.LIGHTCYAN+str(inString)+self.ENDC)
		return inString
	def lightred(self, inString):
		inString = str(self.LIGHTRED+str(inString)+self.ENDC)
		return inString
	def yellow(self, inString):
		inString = str(self.YELLOW+str(inString)+self.ENDC)
		return inString
	def white(self, inString):
		inString = str(self.WHITE+str(inString)+self.ENDC)
		return inString
	def bold(self, inString):
		inString = str(self.BOLD+str(inString)+self.ENDC)
		return inString
	def underline(self, inString):
		inString = str(self.UNDERLINE+str(inString)+self.ENDC)
		return inString

class condorHandler():
	
	"""Object used to open, write, and run a condor vanilla-universe submit file."""
	
	def __init__(self, filename=None, executable=None, title=None, subtitle=None, tertiary=None, c=None):
		
		"""Opens a write job at the filename location. Writes the initial header."""
		
		self.c = c if c is not None else colors()
		colorState = self.c.getState()
		self.filename = filename if filename is not None else sys.exit(c.red('Error: Job filename must be given.'))
		if executable == None: sys.exit(c.red('Error: Job executable must be given.'))
		self.condorJob = open(filename,'w')
		self.logs = []
	
		if colorState: c.disableColors()
		self.condorJob.write('######################################\n')
		self.condorJob.write('#\n')
		self.condorJob.write('# '+title+'\n')
		self.condorJob.write('# '+subtitle+'\n')
		self.condorJob.write('# '+tertiary+'\n')
		self.condorJob.write('# Generated at UTC '+strftime("%Y-%m-%d %H:%M:%S", gmtime())+'\n')
		self.condorJob.write('#\n')
		self.condorJob.write('######################################\n')
		self.condorJob.write('\n')
		self.condorJob.write('Universe   = vanilla\n')
		self.condorJob.write('Executable = '+executable+'\n')
		self.condorJob.write('\n')
		self.condorJob.flush()
		if colorState: c.enableColors()

	def addEntry(self, entries):
		
		"""Takes a dictionary and adds them as condor queue entries."""
		
		colorState = self.c.getState()
	
		if entries == None:
			print(self.c.red('Warning: no entries given in condor header creator. This is probably wrong!'))
	
		if colorState: self.c.disableColors()	
		if 'requirements' in entries:
			self.condorJob.write('requirements'+' = '+entries['requirements']+'\n')
			del entries['requirements']
		if 'output' in entries:
			self.condorJob.write('output'+' = '+entries['output']+'\n')
			del entries['output']
		if 'error' in entries:
			self.condorJob.write('error'+' = '+entries['error']+'\n')
			del entries['error']
		if 'log' in entries:
			self.condorJob.write('log'+' = '+entries['log']+'\n')
			self.logs.append(entries['log'])
			del entries['log']
		if 'arguments' in entries:
			self.condorJob.write('arguments'+' = '+entries['arguments']+'\n')
			del entries['arguments']
	
		if len(entries) > 0:
			for key in entries:
				self.condorJob.write(key+' = '+entries[key]+'\n')
				
		self.condorJob.write('getenv = True\n')
		self.condorJob.write('queue\n')
		self.condorJob.write('\n')
		self.condorJob.flush()
	
		if colorState: self.c.enableColors()
				
	def close(self):
		self.condorJob.close()
		
	def run(self, timeout = None, prepend = '', append = ''):
		if timeout:
			self.starttime = time()
		subprocess.call(prepend+'condor_submit '+self.filename+append, shell=True)
		while len(self.logs) > 0:
			for i, log in enumerate(self.logs):
				if subprocess.run('grep "return" '+log, shell=True).returncode == 0:
					del self.logs[i]
			sleep(1)
			if timeout:
				if (time() - self.starttime) > timeout:
					print(self.c.yellow('Timeout reached. Breaking.'))
					break
					
def runMake3FGL(infile=None, outfile=None, G=None, g=None, I=None, i=None, N=None, e=None, r=None, R=None, ER=None, s=None, v=None, p=None, m=None, GIF=None, ED=None, wd=None, ON=None, P7=None, c=None):
	
	if c is None: c = colors()
	
	if not infile and not outfile:
		sys.exit(c.red('Need a model name!'))
		
	rootString = ['. /nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/fermi-init.sh && python /nfs/optimus/home/zdhughes/Desktop/projects/FermiGalSearch/make3FGLxml.py /nfs/data_links/collaborations/fermi/catalogs/gll_psc_v16.fit '+infile+' -o '+outfile]
	
	if G and g:
		rootString.append('-G '+G+' -g '+g)
	if I and i:
		rootString.append('-I '+I+' -i '+i)
	if N:
		rootString.append('-N')
	if e:
		rootString.append('-e '+e)
	if r:
		rootString.append('-r '+r)
	if R:
		rootString.append('-R '+R)
	if ER:
		rootString.append('-ER '+ER)
	if s:
		rootString.append('-s '+s)
	if v:
		rootString.append('-v '+v)
	if p:
		rootString.append('-p '+p)
	if m:
		rootString.append('-m '+m)
	if GIF:
		rootString.append('-GIF '+GIF)
	if ED:
		rootString.append('-ED '+ED)
	if wd:
		rootString.append('-wd '+wd)
	if ON:
		rootString.append('-ON '+ON)
	if P7:
		rootString.append('-P7 '+P7)
	
	submittedCommand = ' '.join(rootString)
	
	print('Calling:\n\n'+c.purple(submittedCommand)+'\n')
	subprocess.call(submittedCommand, shell=True)
	
def fermiLikelihood(model=None, srcmap=None, livetime=None, expmap=None, outmodel=None, c=None):
	
	if c is None: c = colors()
	
	import pyLikelihood as PL
	import BinnedAnalysis as BA
	
	print('------------------------------')
	print('Printing gtlike parameters:\n')
	print('Input model: '+c.yellow(model))
	print('Source Map: '+c.yellow(srcmap))
	print('Livetime Cube: '+c.yellow(livetime))
	print('Exposure Map: '+c.yellow(expmap))
	print('Output model: '+c.yellow(outmodel))
	print('------------------------------')
			
	observation = BA.BinnedObs(srcmap, livetime, expmap, 'CALDB')
	analysis = BA.BinnedAnalysis(observation, model, optimizer='NewMinuit')
	likeObj = PL.NewMinuit(analysis.logLike)
	analysis.fit(verbosity=4,covar=True,optObject=likeObj)
	print('Ret Code: '+c.red(str(likeObj.getRetCode())))
			
	
	print('Printing fixed source details...')
	print('\n##################################################\n')
	sourceDetails = {}
	for source in analysis.sourceNames():
		sourceDetails[source] = analysis.Ts(source)
				
	for source in analysis.sourceNames():
		if float(analysis.fluxError(source,emin=100)) == 0:
			print(analysis.model[source])
			print('TS: '+str(analysis.Ts(source)))
			print('Flux: '+str(analysis.flux(source,emin=100)))
			print('Flux Error: '+str(analysis.fluxError(source,emin=100))+'\n\n')
				
	print('##################################################\n')
	print('Now printing only freed sources.')
	print('------------------------------------------------------------\n\n')
	for source in analysis.sourceNames():
		if float(analysis.fluxError(source,emin=100)) != 0:
			print(analysis.model[source])
			print('TS: '+str(analysis.Ts(source)))
			print('Flux: '+str(analysis.flux(source,emin=100)))
			print('Flux Error: '+str(analysis.fluxError(source,emin=100))+'\n\n')
	print('------------------------------------------------------------\n\n')
			
	if outmodel:		
		print('Saving xml file as: '+outmodel)
		analysis.logLike.writeXml(outmodel)
	
	
def convertSectionTypes(section):

	"""Converts a dictionary to their most natural types."""
	
	for i, key in enumerate(section):
		try:
			section[key] = ast.literal_eval(section[key])
		except (SyntaxError, ValueError) as e:
			pass
	return section

### Old, do not use. ###

def makeCondorHeader(job=None, executable=None, program=None, stage=None, condorFile=None, c=None):

	if c == None:
		c = colors()

	colorState = c.getState()

	if executable == None:
		sys.exit(c.red('Warning: no executable given in condor header creator.'))
	if job == None:
		sys.exit(c.red('Warning: no job file given in condor header creator.'))

	if colorState:
		c.disableColors()

	job.write('######################################\n')
	job.write('#\n')
	job.write('# '+program+'\n')
	job.write('# '+stage+'\n')
	job.write('# '+condorFile+'\n')
	job.write('# Generated at UTC '+strftime("%Y-%m-%d %H:%M:%S", gmtime())+'\n')
	job.write('#\n')
	job.write('######################################\n')
	job.write('\n')
	job.write('Universe   = vanilla\n')
	job.write('Executable = '+executable+'\n')
	job.write('\n')

	if colorState:
		c.enableColors()

def makeCondorBody(job=None, entries=None, c=None):

	if c == None:
		c = colors()

	colorState = c.getState()

	if job == None:
		sys.exit(c.red('Warning: no job file given in condor header creator.'))
	if entries == None:
		print(c.red('Warning: no entries given in condor header creator. This is probably wrong!'))

	if colorState:
		c.disableColors()

	if 'requirements' in entries:
		job.write('requirements'+' = '+entries['requirements'])
		del entries['requirements']
	if 'output' in entries:
		job.write('output'+' = '+entries['output'])
		del entries['output']
	if 'error' in entries:
		job.write('error'+' = '+entries['error'])
		del entries['error']
	if 'log' in entries:
		job.write('log'+' = '+entries['log'])
		del entries['log']
	if 'arguments' in entries:
		job.write('arguments'+' = '+entries['arguments'])
		del entries['arguments']

	if len(entries) > 0:
		for key in entries:
			job.write(key+' = '+entries[key])
	job.write('getenv = True\n')
	job.write('queue\n')
	job.write('\n')

	if colorState:
		c.enableColors()

def setCommandlineArgs(arguments):

	lineToReturn = ''
	for key in arguments:
		holder = key+'='+str(arguments[key])
		lineToReturn = ' '.join([lineToReturn, holder])
	return lineToReturn


def tryeval(val):
	try:
		val = ast.literal_eval(val)
	except:
		pass
	return val







