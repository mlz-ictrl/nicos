description = 'devices for HP33220a'

# not included by others
group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/hp33220a_2' % nethost

devices = dict(
    hp33220a_amp2 = device('devices.taco.AnalogOutput',
                           description = 'HP33220A #2 amplitude',
                           tacodevice = '%s/amp' % tacodev,
                           abslimits = (0, 1e9),
                          ),
    hp33220a_freq2 = device('devices.taco.AnalogOutput',
                            description = 'HP33220A #2 frequency',
                            tacodevice = '%s/freq' % tacodev,
                            abslimits = (0, 1e9),
                           ),
)

startupcode = """
"""

