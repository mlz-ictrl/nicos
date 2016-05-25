description = 'REFSANS setup for IsegHQ.res'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
#
## rs232server iseg1 exports
#
#    rs232_iseg1 = device('unknown_class:StringIO',
#                         description = 'Device test/rs232/iseg1 of Server rs232server iseg1',
#                         tacodevice = '//%s/test/rs232/iseg1' % nethost,
#                        ),

#
## iseghqserver iseg1 exports
#
    iseg_hv1 = device('devices.taco.VoltageSupply',
                      description = 'Device test/iseg/hv1 of Server iseghqserver iseg1',
                      tacodevice = '//%s/test/iseg/hv1' % nethost,
                      abslimits = (0, 2000),
                      unit = 'V',
                     ),

    iseg_hv1_current = device('devices.taco.AnalogInput',
                              description = 'Device test/iseg/hv1-current of Server iseghqserver iseg1',
                              tacodevice = '//%s/test/iseg/hv1-current' % nethost,
                             ),
)
