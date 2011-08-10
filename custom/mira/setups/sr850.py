includes = ['base', 'lakeshore']

devices = dict(
    M = device('nicos.mira.sr850.Amplifier',
               tacodevice = 'mira/network/samplers2_4'),
)

startupcode = '''
SetDetectors(M)
'''
