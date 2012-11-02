includes = ['system']

nethost = '//toftofsrv.toftof.frm2/'

devices = dict(
    P   = device('devices.taco.io.AnalogInput',
                   tacodevice = nethost + 'toftof/pressure/value',
		   unit = 'bar',
                   pollinterval = 120,
		),
)

startupcode = """
AddEnvironment(P)
"""
