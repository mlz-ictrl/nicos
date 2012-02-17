description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

includes = ['base', 'lakeshore']

devices = dict(
    M = device('nicos.mira.sr850.Amplifier',
               tacodevice = 'mira/network/samplers2_4'),
)

startupcode = '''
SetDetectors(M)
'''
