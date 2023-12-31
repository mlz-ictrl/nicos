description = 'RESEDA NRSE setup'
group = 'basic'
includes = ['reseda', 'det_3he', 'arm_1', 'armcontrol', 'tuning']

startupcode = '''
Exp.measurementmode = 'nrse'
'''
