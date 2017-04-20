description = 'REFSANS setup for psc488ext+rs232-5_06.res'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
#
## rs232server psc488ext exports
#
#    rs232_psc488ext = device('unknown_class:StringIO',
#                             description = 'Device test/rs232/psc488ext of Server rs232server psc488ext',
#                             tacodevice = '//%s/test/rs232/psc488ext' % nethost,
#                            ),

#
## hpe3631aserver gkssmagnet exports
#
    delta_current = device('devices.taco.CurrentSupply',
                           description = 'Device test/delta/current of Server hpe3631aserver gkssmagnet',
                           tacodevice = '//%s/test/delta/current' % nethost,
                           abslimits = (0, 100),
                          ),

    delta_voltage = device('devices.taco.AnalogInput',
                           description = 'Device test/delta/voltage of Server hpe3631aserver gkssmagnet',
                           tacodevice = '//%s/test/delta/voltage' % nethost,
                          ),

)
