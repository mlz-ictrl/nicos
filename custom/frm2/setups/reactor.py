description = 'FRM II reactor status devices'

group = 'lowlevel'

nethost = 'tacodb.taco.frm2'

devices = dict(
    ReactorPower = device('nicos.taco.AnalogInput',
                          description = 'The FRM II reactor power',
                          tacodevice = '//%2/frm2/reactor/power' % (nethost, ),
                          fmtstr = '%.1f',
                          pollinterval = 60,
                          tacotimeout = 0.5,
                          maxage = 3600,
                          unit = 'MW'),

#    ColdSrc  = device('nicos.taco.AnalogInput',
#                      description = 'Temperature of the cold source',
#                      tacodevice = '//%s/frm2/coldsource/temp' % (nethost, ),
#                      pollinterval = 60,
#                      maxage = 120),

#    HotSrc   = device('nicos.taco.AnalogInput',
#                      description = 'Temperature of the hot source',
#                      tacodevice = '//%s/frm2/hotsource/temp' % (nethost, ),
#                      pollinterval = 60,
#                      maxage = 120),
)

startupcode = """
"""

