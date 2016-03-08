description = 'FRM-II reactor status devices'

group = 'lowlevel'

nethost = 'tacodb.taco.frm2'

devices = dict(
    ReactorPower = device('devices.taco.AnalogInput',
                          description = 'FRM-II reactor power',
                          tacodevice = '//%s/frm2/reactor/power' % (nethost, ),
                          warnlimits = (19, 21),
                          fmtstr = '%.1f',
                          pollinterval = 60,
                          maxage = 3600,
                          unit = 'MW'),

#    ColdSrc  = device('devices.taco.AnalogInput',
#                      description = 'Temperature of the cold source',
#                      tacodevice = '//%s/frm2/coldsource/temp' % (nethost, ),
#                      pollinterval = 60,
#                      maxage = 120),

#    HotSrc   = device('devices.taco.AnalogInput',
#                      description = 'Temperature of the hot source',
#                      tacodevice = '//%s/frm2/hotsource/temp' % (nethost, ),
#                      pollinterval = 60,
#                      maxage = 120),
)
