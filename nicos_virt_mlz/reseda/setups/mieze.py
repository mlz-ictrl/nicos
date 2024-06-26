description = 'RESEDA MIEZE setup'
group = 'basic'
includes = [
    'reseda', 'det_cascade', 'arm_1', 'armcontrol', 'attenuators',
    'slitsng', 'tuning'
]

startupcode = '''
SetDetectors(psd)
psd_channel.mode = 'tof'
Exp.measurementmode = 'mieze'
'''
