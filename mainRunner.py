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
from multiprocessing import Pool, Lock

import sys
import code
from os import getcwd, chdir

def doStages(member):
	print('Working on section '+c.green(member)+'. Making directores...')
	print('Top section directory '+c.yellow(handler[member].topConfig['directory']))
	subprocess.call('mkdir -p '+handler[member].topConfig['directory'], shell=True)
	print('Model directory '+c.yellow(handler[member].topConfig['modelDir']))
	subprocess.call('mkdir -p '+handler[member].topConfig['modelDir'], shell=True)	
	
	#Check if its a nonlightcurve section, i.e. just one time period.
	if len(handler[member].range) == 1:
		
		handler[member].setDefaults(inter=member, likemodel=handler.generalSection['likemodel'])
		
		for doSection in handler[member].topSection:
			
			if handler[member].topSection[doSection] == True:
				
				print(c.lightgreen(doSection)+' set to '+c.lightblue(handler[member].topSection[doSection])+' in section '+c.green(member))
				
				if handler.generalSection['verbosity'] == '2':
					handler[member].printSection(doSection)
										 				
				if doSection == 'doModel':
					GFF.runMake3FGL(**handler[member].childConfig['doModel'], c=handler.c)
					continue
				
				if doSection == 'doResidual':
					currentDir = getcwd()
					chdir(handler[member].topConfig['directory'])
					subprocess.call('farith '+handler[member].childConfig['doResidual']['infile1']+' '+handler[member].childConfig['doResidual']['infile2']+' '+handler[member].childConfig['doResidual']['outfile']+' SUB',shell=True)
					chdir(currentDir)
					continue
				
				job, executable, textDir, entries = GFF.getCondorFermiParameters(handler[member].topConfig['directory'], doSection, handler[member].saveName[0], likemodel = handler.generalSection['likemodel'])
				subprocess.call('mkdir '+textDir, shell=True)

				print('Using these parameters for the condor submit file:\n Job: '+c.yellow(job)+'\n executable: '+c.purple(executable)+'\n textDir: '+c.yellow(textDir)+'\n')
				

				entries['arguments'] = GFF.setCommandlineArgs(handler[member].getChildSection(doSection))
				entries['requirements'] = '(machine == "herc0")'
				
				if doSection == 'doLike':
					entries['arguments'] = ' '.join(['/nfs/optimus/home/zdhughes/Desktop/projects/FermiGalSearch/fermiLikelihood.py', entries['arguments']])
				
				condorJob = GFF.condorHandler(filename=job, executable=executable, title=calling_program, subtitle=executable.split('/')[-1], tertiary=handler[member].saveName[0], c=handler.c)
				condorJob.addEntry(entries)
				condorJob.close()
				

				if handler.generalSection['run'] == True:
					condorJob.run(prepend='. /nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/fermi-init.sh && ')
				
			else:
				print(c.lightgreen(doSection)+' set to '+c.lightred(handler[member].topSection[doSection])+' in section '+c.green(member))	
	else:
		for doSection in handler[member].topSection:		
			if handler[member].topSection[doSection] == True:
				print(c.lightgreen(doSection)+' set to '+c.lightblue(handler[member].topSection[doSection])+' in section '+c.green(member))
				for i, increment in enumerate(handler[member].times):
					handler[member].setDefaults(inter=member, likemodel=handler.generalSection['likemodel'], increment=increment[0])
					if int(handler.generalSection['verbosity']) == 2:
						handler[member].printSection(doSection)					 				
					elif doSection == 'doModel':
						GFF.runMake3FGL(**handler[member].childConfig['doModel'], c=handler.c)
					elif doSection == 'doResidual':
						currentDir = getcwd()
						chdir(handler[member].topConfig['directory'])
						subprocess.call('farith '+handler[member].childConfig['doResidual']['infile1']+' '+handler[member].childConfig['doResidual']['infile2']+' '+handler[member].childConfig['doResidual']['outfile']+' SUB',shell=True)
						chdir(currentDir)
					else:
						if doSection == 'doFilter':
							handler[member].childConfig[doSection]['tmin'] = str(increment[0])
							handler[member].childConfig[doSection]['tmax'] = str(increment[1])
						job, executable, textDir, entries = GFF.getCondorFermiParameters(handler[member].topConfig['directory'], doSection, handler[member].saveName[i], likemodel = handler.generalSection['likemodel'])
						if i == 0:
							subprocess.call('mkdir '+textDir, shell=True)
						if int(handler.generalSection['verbosity']) >= 1: 
							print('Using these parameters for the condor submit file:\n Job: '+c.yellow(job)+'\n executable: '+c.purple(executable)+'\n textDir: '+c.yellow(textDir)+'\n')
						entries['arguments'] = GFF.setCommandlineArgs(handler[member].getChildSection(doSection))
						#entries['requirements'] = '(machine == "herc0")'
						if doSection == 'doLike':
							entries['arguments'] = ' '.join(['/nfs/optimus/home/zdhughes/Desktop/projects/FermiGalSearch/fermiLikelihood.py', entries['arguments']])
						if i == 0:
							condorJob = GFF.condorHandler(filename=job, executable=executable, title=calling_program, subtitle=executable.split('/')[-1], tertiary=handler[member].saveName[i], c=handler.c)
						condorJob.addEntry(entries)
				if bool(handler.generalSection['run']) == True and doSection not in ['doModel', 'doResidual']:
					condorJob.run(prepend='. /nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/fermi-init.sh && ')
				if doSection not in ['doModel', 'doResidual']:
					condorJob.close()
			else:
				print(c.lightgreen(doSection)+' set to '+c.lightred(handler[member].topSection[doSection])+' in section '+c.green(member))


		

#Command line variables
calling_program, masterConigFilename = sys.argv

#Create handler
handler = ch.ecumenical(calling_program, masterConigFilename)
c = handler.c

print(c.lightblue('\n+++++++++++ RUNNER +++++++++++\n\n'))
print('Creating working directory '+c.yellow(handler.generalSection['workingDir']))
subprocess.call('mkdir -p '+handler.generalSection['workingDir'], shell=True)

pool = Pool()
results = [pool.apply_async(doStages, args=(x,)) for x in list(handler.members)]
output = [p.get() for p in results]





#results = pool.map(doStuff, list(handler.members))
#pool.close() 
#pool.join()





#code.interact(local=locals())
#sys.exit('Code Break!')		 
