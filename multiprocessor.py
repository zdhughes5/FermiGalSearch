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

def doSections(member):
	
	print('Working on selection '+c.green(member.selectionName)+'. Making directores...')
	print('Selection directory '+c.yellow(member.parameters['directory']))
	subprocess.call('mkdir -p '+member.parameters['directory'], shell=True)
	print('Model directory '+c.yellow(member.parameters['modelDir']))
	subprocess.call('mkdir -p '+member.parameters['modelDir'], shell=True)
		
	if len(member.range) == 1:
		for stage in member.stages:
			if member.stages[stage] == True:
				print(c.lightgreen(stage)+' set to '+c.lightblue(member.stages[stage])+' in selection '+c.green(member.selectionName))
				member.setDefaults(inter=member.selectionName, likemodel=member.general['likemodel'])
				if member.general['verbosity'] == 2:
					member.printSection(stage)
				if stage == 'doModel':
					GFF.runMake3FGL(**member.childConfig['doModel'], c=handler.c)
					continue
				elif stage == 'doResidual':
					currentDir = getcwd()
					chdir(member.parameters['directory'])
					subprocess.call('farith '+member.childConfig['doResidual']['infile1']+' '+member.childConfig['doResidual']['infile2']+' '+member.childConfig['doResidual']['outfile']+' SUB',shell=True)
					chdir(currentDir)
					continue
				else:
					job, executable, textDir, entries = GFF.getCondorFermiParameters(member.parameters['directory'], stage, member.saveName[0], likemodel = member.general['likemodel'])
					if member.general['verbosity'] >= 1:
						print('Using these parameters for the condor submit file:\n Job: '+c.yellow(job)+'\n executable: '+c.purple(executable)+'\n textDir: '+c.yellow(textDir)+'\n')
					subprocess.call('mkdir '+textDir, shell=True)
					entries['arguments'] = GFF.setCommandlineArgs(member.getSettings(stage))
					entries['requirements'] = '(machine == "herc0")'
					if stage == 'doLike':
						entries['arguments'] = ' '.join(['/nfs/optimus/home/zdhughes/Desktop/projects/FermiGalSearch/fermiLikelihood.py', entries['arguments']])
					condorJob = GFF.condorHandler(filename=job, executable=executable, title=calling_program, subtitle=executable.split('/')[-1], tertiary=handler[member].saveName[0], c=handler.c)
					condorJob.addEntry(entries)
					condorJob.close()
					if handler.generalSection['run'] == True:
						condorJob.run(prepend='. /nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/fermi-init.sh && ')
			else:
				print(c.lightgreen(stage)+' set to '+c.lightred(member.stages[stage])+' in section '+c.green(member.selectionName))	
	else:
		for stage in member.stages:		
			if member.stages[stage] == True:
				print(c.lightgreen(stage)+' set to '+c.lightblue(member.stages[stage])+' in section '+c.green(member.selectionName))
				for i, increment in enumerate(member.times):
					member.setDefaults(inter=member.selectionName, likemodel=member.general['likemodel'], increment=increment[0])
					if int(member.general['verbosity']) == 2:
						member.printSettings(stage)					 				
					if stage == 'doModel':
						GFF.runMake3FGL(**member.childConfig['doModel'], c=handler.c)
					elif stage == 'doResidual':
						currentDir = getcwd()
						chdir(member.parameters['directory'])
						subprocess.call('farith '+member.childConfig['doResidual']['infile1']+' '+member.childConfig['doResidual']['infile2']+' '+member.childConfig['doResidual']['outfile']+' SUB',shell=True)
						chdir(currentDir)
					else:
						if stage == 'doFilter':
							member.childConfig[stage]['tmin'] = str(increment[0])
							member.childConfig[stage]['tmax'] = str(increment[1])
						job, executable, textDir, entries = GFF.getCondorFermiParameters(member.parameters['directory'], stage, member.saveName[i], likemodel = member.general['likemodel'])
						if member.general['verbosity'] >= 1: 
							print('Using these parameters for the condor submit file:\n Job: '+c.yellow(job)+'\n executable: '+c.purple(executable)+'\n textDir: '+c.yellow(textDir)+'\n')						
						if i == 0:
							subprocess.call('mkdir '+textDir, shell=True)
						entries['arguments'] = GFF.setCommandlineArgs(member.getSettings(stage))
						#entries['requirements'] = '(machine == "herc0")'
						if stage == 'doLike':
							entries['arguments'] = ' '.join(['/nfs/optimus/home/zdhughes/Desktop/projects/FermiGalSearch/fermiLikelihood.py', entries['arguments']])
						if i == 0:
							condorJob = GFF.condorHandler(filename=job, executable=executable, title=calling_program, subtitle=executable.split('/')[-1], tertiary=member.saveName[i], c=handler.c)
						condorJob.addEntry(entries)
				if bool(member.general['run']) == True and stage not in ['doModel', 'doResidual']:
					condorJob.run(prepend='. /nfs/programs/fermi/v10r0p5/x86_64-unknown-linux-gnu-libc2.17/fermi-init.sh && ')
				if stage not in ['doModel', 'doResidual']:
					condorJob.close()
			else:
				print(c.lightgreen(stage)+' set to '+c.lightred(member.stages[stage])+' in section '+c.green(member.selectionName))

#Command line variables
calling_program, masterConigFilename = sys.argv

#Create handler
handler = ch.ecumenical(calling_program, masterConigFilename)
c = handler.c

print(c.lightblue('\n+++++++++++ RUNNER +++++++++++\n\n'))
print('Creating working directory '+c.yellow(handler.general['workingDir']))
subprocess.call('mkdir -p '+handler.general['workingDir'], shell=True)

pool = Pool()
results = [pool.apply_async(doSections, args=(x,)) for x in handler.to_list()]
output = [p.get() for p in results]





#results = pool.map(doStuff, list(handler.members))
#pool.close() 
#pool.join()





#code.interact(local=locals())
#sys.exit('Code Break!')		 
