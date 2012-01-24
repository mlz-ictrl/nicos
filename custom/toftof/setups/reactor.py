description = 'reactor power readout'
includes = ['system']

devices = dict(
    ReactorPower = device('nicos.taco.io.AnalogInput',
                          tacodevice = '//tacodb.taco.frm2/frm2/reactor/power',
                          fmtstr = '%5.1f',
                          pollinterval = 30,
                          maxage = 40),
)
