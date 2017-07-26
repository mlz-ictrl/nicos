#  -*- coding: utf-8 -*-

description = 'RESEDA NRSE setup'
group = 'basic'
includes = ['reseda', 'det_3he', 'nrse_subcoil', 'arm0a', 'arm1', 'tuning']

startupcode = '''
Exp.measurementmode = 'nrse'
'''
