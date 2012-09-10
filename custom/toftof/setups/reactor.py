description = 'reactor power readout'
includes = ['system']

devices = dict(
    ReactorPower = device('nicos.taco.io.AnalogInput',
                          tacodevice = '//tacodb.taco.frm2/frm2/reactor/power',
                          # tacodevice = '//toftofsrv/toftof/reactor/power',
                          fmtstr = '%5.1f',
                          pollinterval = 60,
                          maxage = 80),
#    ReactorPower = device('nicos.toftof.power.Power', raw='ReactorPowerRaw', unit='MW', fmtstr='%5.1f', pollinterval=30, maxage=40),
)
