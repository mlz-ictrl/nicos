description = 'high voltage power supplies for detector'

group = 'lowlevel'

includes = []

nethost = 'localhost'

devices = dict(
    hv0   = device('nicos.devices.taco.VoltageSupply',
                   description = 'ISEG HV power supply 1',
                   # requires = {'level': 'admin'},
                   tacodevice = '//%s/del/iseg1/voltage' % (nethost,),
                   abslimits = (0, 3000),
                   ramp = 120,
                   pollinterval = 5,
                   maxage = 61,
                  ),
    hv0cur = device('nicos.devices.taco.AnalogInput',
                    description = 'ISEG HV power supply 1 (current)',
                    tacodevice = '//%s/del/iseg1/current' % (nethost,),
                    pollinterval = 5,
                    maxage = 61,
                    fmtstr = '%.3f',
                   ),
    hv1   = device('nicos.devices.taco.VoltageSupply',
                   description = 'ISEG HV power supply 2',
                   # requires = {'level': 'admin'},
                   tacodevice = '//%s/del/iseg2/voltage' % (nethost,),
                   abslimits = (0, 3000),
                   ramp = 120,
                   pollinterval = 5,
                   maxage = 61,
                  ),
    hv1cur = device('nicos.devices.taco.AnalogInput',
                    description = 'ISEG HV power supply 1 (current)',
                    tacodevice = '//%s/del/iseg2/current' % (nethost,),
                    pollinterval = 5,
                    maxage = 61,
                    fmtstr = '%.3f',
                   ),
)
