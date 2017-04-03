description = 'at samplecamper [slit k1]'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
#
## rs232server b2 exports
#
#    rs232_b2 = device('unknown_class:StringIO',
#                      description = 'Device test/rs232/b2 of Server rs232server b2',
#                      tacodevice = '//%s/test/rs232/b2' % nethost,
#                     ),

#
## smccorvusserver b2 exports
#
    b2r    = device('devices.generic.Axis',
                    description = 'b2, reactorside',
                    motor = 'smccorvus_b2mr',
                    precision = 0.0,
                   ),
    b2s    = device('devices.generic.Axis',
                    description = 'b2, sampleside',
                    motor = 'smccorvus_b2ms',
                    precision = 0.0,
                   ),
    smccorvus_b2er = device('devices.taco.Coder',
                            description = 'Device test/smccorvus/b2er of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2er' % nethost,
                            lowlevel = True,
                           ),

    smccorvus_b2mr = device('devices.taco.Motor',
                            description = 'Device test/smccorvus/b2mr of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2mr' % nethost,
                            abslimits = (-294, 222),
                            lowlevel = True,
                           ),

    smccorvus_b2es = device('devices.taco.Coder',
                            description = 'Device test/smccorvus/b2es of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2es' % nethost,
                            lowlevel = True,
                           ),

    smccorvus_b2ms = device('devices.taco.Motor',
                            description = 'Device test/smccorvus/b2ms of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2ms' % nethost,
                            abslimits = (-296, 213),
                            lowlevel = True,
                           ),

)
