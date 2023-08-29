description = 'Heater for ZEBRA Battery'

group = 'optional'

tango_base = 'tango://mpfc01.antares.frm2.tum.de:10000/'

devices = dict(
    T1 = device('nicos.devices.entangle.TemperatureController',
        description = 'The control device to the sample',
        tangodevice = tango_base + 'mpfc/ls340/control1',
        abslimits = (0, 800),
        unit = 'C',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    T2 = device('nicos.devices.entangle.TemperatureController',
        description = 'The control device to the sample',
        tangodevice = tango_base + 'mpfc/ls340/control2',
        abslimits = (0, 800),
        unit = 'C',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
)

startupcode = '''
AddEnvironment(T1, T2)
'''
