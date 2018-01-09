#  -*- coding: utf-8 -*-

description = 'RESEDA MIEZE setup'
group = 'basic'
includes = [
    'reseda', 'det_cascade', 'arm_0a', 'arm_0b', 'arm_2', 'slits',
    'attenuators', 'slitsng', 'tuning'
]

startupcode = '''
Exp.measurementmode = 'mieze'
'''
