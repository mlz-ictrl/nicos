#  -*- coding: utf-8 -*-

description = 'RESEDA MIEZE setup'
group = 'basic'
includes = [
    'reseda', 'det_cascade', 'mieze_subcoil', 'arm0a', 'arm0b', 'arm2', 'tuning'
]

startupcode = '''
Exp.measurementmode = 'mieze'
'''
