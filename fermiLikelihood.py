# -*- coding: utf-8 -*-
"""
Created on Mon May  1 15:04:10 2017

@author: zdhughes
"""

import sys
import os
import general_functions_fermi as GFF
import code

import pyLikelihood as PL
import BinnedAnalysis as BA
from UpperLimits import UpperLimits

class tee:
	
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

for item in sys.argv[1:]:
	print(item)

options = {}
for option in sys.argv[1:]:
	options[option.split('=')[0]] = option.split('=')[1]

savedStdout = sys.stdout
file = open(options['results'],'w')
sys.stdout = tee(savedStdout, file)
	
print('------------------------------')
print('Printing gtlike parameters:\n')
print('Input model: '+options['srcmdl'])
print('Source Map: '+options['srcmap'])
print('Livetime Cube: '+options['expcube'])
print('Exposure Map: '+options['bexpmap'])
print('Output model: '+options['outmodel'])
print('------------------------------')
sys.stdout.flush()
		
observation = BA.BinnedObs(srcMaps=options['srcmap'], expCube=options['expcube'], binnedExpMap=options['bexpmap'], irfs='CALDB')
analysis = BA.BinnedAnalysis(binnedData=observation, srcModel=options['srcmdl'], optimizer=options['optimizer'], psfcorr=bool(options['psfcorr']))
likeObj = PL.NewMinuit(analysis.logLike)
analysis.fit(verbosity=4,covar=True, optObject=likeObj, tol=float(options['ftol']))
print('Ret Code: '+str(likeObj.getRetCode()))
sys.stdout.flush()	

print('Printing fixed source details...')
print('\n##################################################\n')
sourceDetails = {}
for source in analysis.sourceNames():
	sourceDetails[source] = analysis.Ts(source)
			
for source in analysis.sourceNames():
	if float(analysis.fluxError(source,emin=float(options['emin']))) == 0.:
		print(analysis.model[source])
		print('TS: '+str(analysis.Ts(source)))
		print('Flux: '+str(analysis.flux(source,emin=float(options['emin']))))
		print('Flux Error: '+str(analysis.fluxError(source,emin=float(options['emin'])))+'\n\n')
		sys.stdout.flush()
			
print('##################################################\n')
print('Now printing only freed sources.')
print('------------------------------------------------------------\n\n')
for source in analysis.sourceNames():
	if float(analysis.fluxError(source,emin=float(options['emin']))) != 0.:
		print(analysis.model[source])
		print('TS: '+str(analysis.Ts(source)))
		print('Flux: '+str(analysis.flux(source,emin=float(options['emin']))))
		print('Flux Error: '+str(analysis.fluxError(source,emin=float(options['emin'])))+'\n\n')
		sys.stdout.flush()
print('------------------------------------------------------------\n\n')
		
print('Saving counts spectra as: '+options['specfile'])
analysis.writeCountsSpectra(outfile=options['specfile'])

print('Saving xml file as: '+options['outmodel'])
analysis.logLike.writeXml(options['outmodel'])