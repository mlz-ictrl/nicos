#  -*- coding: utf-8 -*-

description = 'RESEDA MIEZE setup'
group = 'basic'
includes = [
    'reseda', 'det_cascade', 'mieze_subcoil', 'arm_0a', 'arm_0b', 'arm_2', 'tuning'
]

startupcode = '''
Exp.measurementmode = 'mieze'
'''
