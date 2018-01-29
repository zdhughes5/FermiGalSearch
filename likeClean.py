#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May  1 15:04:10 2017

@author: zdhughes
"""

import sys
import os
import general_functions_fermi as GFF

import pyLikelihood as PL
import BinnedAnalysis as BA
from UpperLimits import UpperLimits


options = {}
for option in sys.argv:
	options[option.split('=')[0]] = option.split('=')[1]

if option['write'] == 'True':
	sys.stdout = open(option['fileout'],'w')

print('------------------------------')
print('Printing gtlike parameters:\n')
print('Input model: '+options['model'])
print('Source Map: '+options['srcmap'])
print('Livetime Cube: '+options['livetime'])
print('Exposure Map: '+options['expmap'])
print('Output model: '+options['outmodel'])
print('------------------------------')
		
observation = BA.BinnedObs(options['srcmap'], options['livetime'], options['expmap'], 'CALDB')
analysis = BA.BinnedAnalysis(observation, options['model'], optimizer='NewMinuit')
likeObj = PL.NewMinuit(analysis.logLike)
analysis.fit(verbosity=4,covar=True,optObject=likeObj)
print('Ret Code: '+str(likeObj.getRetCode()))
		

print('Printing fixed source details...')
print('\n##################################################\n')
sourceDetails = {}
for source in analysis.sourceNames():
	sourceDetails[source] = analysis.Ts(source)
			
for source in analysis.sourceNames():
	if float(analysis.fluxError(source,emin=options['emin'])) == 0:
		print(analysis.model[source])
		print('TS: '+str(analysis.Ts(source)))
		print('Flux: '+str(analysis.flux(source,emin=options['emin'])))
		print('Flux Error: '+str(analysis.fluxError(source,emin=options['emin']))+'\n\n')
			
print('##################################################\n')
print('Now printing only freed sources.')
print('------------------------------------------------------------\n\n')
for source in analysis.sourceNames():
	if float(analysis.fluxError(source,emin=options['emin'])) != 0:
		print(analysis.model[source])
		print('TS: '+str(analysis.Ts(source)))
		print('Flux: '+str(analysis.flux(source,emin=options['emin'])))
		print('Flux Error: '+str(analysis.fluxError(source,emin=options['emin']))+'\n\n')
print('------------------------------------------------------------\n\n')
		
		
print('Saving xml file as: '+options['outmodel'])
analysis.logLike.writeXml(options['outmodel'])