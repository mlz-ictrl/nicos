#  -*- coding: utf-8 -*-

description = 'RESEDA NRSE setup'
group = 'basic'
includes = ['reseda', 'det_3he', 'nrse_subcoil', 'arm_0', 'armcontrol', 'tuning']

startupcode = '''
Exp.measurementmode = 'nrse'
'''
