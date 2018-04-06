#  -*- coding: utf-8 -*-

description = 'RESEDA NRSE setup'
group = 'basic'
includes = ['reseda', 'det_3he', 'nrse_subcoil', 'arm_0a','arm_0b', 'arm_1', 'arm_2', 'tuning']

startupcode = '''
Exp.measurementmode = 'nrse'
'''
