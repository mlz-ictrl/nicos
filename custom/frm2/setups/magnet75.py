description = 'FRM II 7.5 T superconducting magnet'

group = 'optional'

includes = ['alias_B']

nethost = 'magnet'

devices = dict(
    B_m7T5  = device('devices.taco.CurrentSupply',
                     description = 'The magnetic field',
                     tacodevice = '//%s/magnet/smc120/t' % (nethost,),
                     abslimits = (-7.5, 7.5),
                    ),

    sth_m7T5_ccr = device('devices.taco.Axis',
                          description = 'Cryotstat tube rotation',
                          tacodevice = '//%s/magnet/axis/tube' % (nethost,),
                          abslimits = (-180, 180),
                         ),

    sth_m7T5_stick = device('devices.taco.Axis',
                            description = 'Cryotstat stick rotation',
                            tacodevice = '//%s/magnet/axis/stick' % (nethost,),
                            abslimits = (-180, 180),
                           ),
)

descriptions = ['', '', '', '', '', '', '', '', '']
# Maximum temeratures for field operation above 80A (6.6T) taken from the manual
maxtemps = [None, 4.3, 4.3, 5.1, 4.7, None, None, None, 4.3]

for i in range(1, 9):
    devices['m7T5_T%d' % i] = device('devices.taco.TemperatureSensor',
                                     description = '7.5T magnet temperature sensor %d (%s)' % (i, descriptions[i]),
                                     tacodevice = '//%s/magnet/ls218/sens%d' % (nethost, i),
                                     warnlimits = (0, maxtemps[i]),
                                     pollinterval = 30,
                                     maxage = 90,
                                     unit = 'K',
                                    )

startupcode = """
B.alias = B_m7T5
"""
