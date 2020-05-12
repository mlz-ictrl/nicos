#  -*- coding: utf-8 -*-

description = 'RESEDA MIEZE setup with resedacascade2 detector (7 foils)'
group = 'basic'
includes = [
    'reseda', 'det_cascade2', 'arm_0', 'armcontrol', 'attenuators',
    'slitsng', 'tuning'
]

startupcode = '''
Exp.measurementmode = 'mieze'
'''
