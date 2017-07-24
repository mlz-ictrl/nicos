description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

includes = ['base']

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    M = device('nicos_mlz.mira.devices.sr850.Amplifier',
               description = 'SR850 lock-in amplifier',
               tangodevice = tango_base + 'sr850/io',
              ),
    M2 = device('nicos_mlz.mira.devices.sr850.Amplifier',
               description = 'SR850 lock-in amplifier',
               tangodevice = tango_base + 'sr850/io2',
              ),
)

startupcode = '''
SetDetectors(M, M2)
'''
