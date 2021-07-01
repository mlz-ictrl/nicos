#  -*- coding: utf-8 -*-

description = 'RESEDA NRSE setup'
group = 'basic'
includes = ['reseda', 'det_3he', 'arm_0', 'armcontrol', 'tuning']

startupcode = '''
Exp.measurementmode = 'nrse'
'''
