includes = ['system']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    P   = device('devices.taco.AnalogInput',
                   tacodevice = '//%s/toftof/pressure/value' % (nethost,),
		   unit = 'bar',
                   pollinterval = 120,
		),
)

startupcode = """
AddEnvironment(P)
"""
