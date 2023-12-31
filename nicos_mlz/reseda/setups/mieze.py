description = 'RESEDA MIEZE setup with resedacascade detector (6-foils)'
group = 'basic'
includes = [
    'reseda', 'det_cascade', 'arm_1', 'armcontrol', 'attenuators',
    'slitsng', 'tuning'
]

startupcode = '''
Exp.measurementmode = 'mieze'
'''
