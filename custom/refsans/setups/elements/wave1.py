description = 'Funktionsgenerator HP33220'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
#
## hp33250aserver wave1 exports
#
    hp33220a_1_freq = device('devices.taco.AnalogOutput',
                             description = 'freq of wave1',
                             tacodevice = '//%s/test/hp33220a_1/freq' % nethost,
                             abslimits = (0, 1e6),
                            ),

    hp33220a_1_amp = device('devices.taco.AnalogOutput',
                            description = 'amp of wave1',
                            tacodevice = '//%s/test/hp33220a_1/amp' % nethost,
                            abslimits = (0, 10),
                           ),

)
