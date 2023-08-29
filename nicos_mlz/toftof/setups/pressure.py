description = 'Setup for the pressure cell'

group = 'optional'

tango_base = 'tango://toftofsrv.toftof.frm2.tum.de:10000/'

devices = dict(
    P = device('nicos.devices.entangle.Sensor',
        description = 'Pressure cell device',
        tangodevice = tango_base + 'toftof/pressure/value',
        unit = 'bar',
        pollinterval = 120,
    ),
)

startupcode = '''
AddEnvironment(P)
'''
