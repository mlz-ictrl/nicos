description = 'Funktionsgenerator HP33220'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
#
## hp33250aserver wave2 exports
#
    hp33220a_2_freq = device('devices.taco.AnalogOutput',
                             description = 'freq of wave2',
                             tacodevice = '//%s/test/hp33220a_2/freq' % nethost,
                             abslimits = (0, 1e6),
                            ),

    hp33220a_2_amp = device('devices.taco.AnalogOutput',
                            description = 'amp of wave2',
                            tacodevice = '//%s/test/hp33220a_2/amp' % nethost,
                            abslimits = (0, 10),
                           ),

)
