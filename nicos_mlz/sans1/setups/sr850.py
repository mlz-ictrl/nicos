description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/'

devices = dict(
    M = device('nicos_mlz.mira.devices.sr850.Amplifier',
        description = 'SR850 lock-in amplifier',
        #tangodevice = tango_base + 'sr850/io',
        #tangodevice = tango_base + 'sr850/gpib_io1',
        tangodevice = tango_base + 'sr850/moxa_io1',
    ),
    M2 = device('nicos_mlz.mira.devices.sr850.Amplifier',
        description = 'SR850 lock-in amplifier',
        #tangodevice = tango_base + 'sr850/io2',
        #tangodevice = tango_base + 'sr850/gpib_io2',
        tangodevice = tango_base + 'sr850/moxa_io2',
    ),
)

startupcode = '''
SetDetectors(M, M2)
'''
