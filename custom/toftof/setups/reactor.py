description = 'reactor power readout'

includes = ['system']

nethost = 'tacodb.taco.frm2'

devices = dict(
    ReactorPower = device('devices.taco.AnalogInput',
                          tacodevice = '//%s/frm2/reactor/power' % (nethost, ),
                          # tacodevice = '//toftofsrv/toftof/reactor/power',
                          fmtstr = '%5.1f',
                          pollinterval = 60,
                          maxage = 80,
                         ),
#    ReactorPower = device('toftof.power.Power', raw='ReactorPowerRaw', unit='MW', fmtstr='%5.1f', pollinterval=30, maxage=40),
)
