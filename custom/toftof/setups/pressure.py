description = 'Setup for the pressure cell'

group = 'optional'

includes = []

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    P   = device('devices.taco.AnalogInput',
                 description = 'Pressure cell device',
                 tacodevice = '//%s/toftof/pressure/value' % (nethost,),
                 unit = 'bar',
                 pollinterval = 120,
                ),
)

startupcode = '''
AddEnvironment(P)
'''
