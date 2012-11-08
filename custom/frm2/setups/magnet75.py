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

    m7T5_motor_p = device('devices.taco.Motor',
                          description = 'The Cryostat rotation motor (Phytron)',
                          tacodevice = '//%s/magnet/phytron/motor' % (nethost,),
                          abslimits = (-360, 360),
                          userlimits = (-40, 40),
                          lowlevel = True,
                         ),

    m7T5_coder_p = device('devices.taco.Coder',
                          description = 'The Cryostat rotation encoder (Phytron)',
                          tacodevice = '//%s/magnet/phytron/encoder' % (nethost, ),
                          lowlevel = True,
                         ),

    m7T5_axis_p = device('devices.generic.Axis',
                         description = 'The Cryostat rotation (Phytron)',
                         motor = 'm7T5_motor_p',
                         coder = 'm7T5_coder_p',
                         obs = [],
                         precision = 0.01,
                         backlash = -1,
                        ),

    m7T5_motor_n = device('devices.taco.Motor',
                          description = 'The Sample stick rotation motor (Newport)',
                          tacodevice = '//%s/magnet/newportmc/motor' % (nethost,),
                          abslimits = (-180, 180),
                          lowlevel = True,
                         ),

    m7T5_coder_n = device('devices.taco.Coder',
                          description = 'The Sample stick rotation encoder (Newport)',
                          tacodevice = '//%s/magnet/newportmc/encoder' % (nethost, ),
                          lowlevel = True,
                         ),

    m7T5_axis_n = device('devices.generic.Axis',
                         description = 'The Sample stick rotation (Newport)',
                         motor = 'm7T5_motor_n',
                         coder = 'm7T5_coder_n',
                         obs = [],
                         precision = 0.01,
                         backlash = -0.1,
                        ),
)

descriptions = ['',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
               ]

for i in range(1, 9):
    devices['m7T5_T%d' % i] = device('devices.taco.TemperatureSensor',
                                     description = '7.5T magnet temperature sensor %d (%s)' % (i, descriptions[i]),
                                     tacodevice = '//%s/magnet/ls218/sens%d' % (nethost, i),
                                     pollinterval = 30,
                                     unit = 'K',
                                    )

startupcode = """
B.alias = B_m7T5
"""
