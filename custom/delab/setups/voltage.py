description = 'high voltage power supplies for detector'

group = 'lowlevel'

includes = []

nethost = 'deldaq50.del.frm2'

devices = dict(
    hv0   = device('devices.taco.VoltageSupply',
                   description = 'ISEG HV power supply 1',
                   requires = {'level': 'admin'},
                   tacodevice = '//%s/del/iseg1/voltage' % (nethost,),
                   abslimits = (0, 1600),
                   ramp = 120,
                   pollinterval = 60,
                  ),
    hv1   = device('devices.taco.VoltageSupply',
                   description = 'ISEG HV power supply 2',
                   requires = {'level': 'admin'},
                   tacodevice = '//%s/del/iseg2/voltage' % (nethost,),
                   abslimits = (0, 1600),
                   ramp = 120,
                   pollinterval = 60,
                  ),
)
