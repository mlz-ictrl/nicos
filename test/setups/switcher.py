name = 'test switcher'

includes = ['system']

devices = dict(

    motor_1 = device(
        'nicos.virtual.VirtualMotor',
        unit = 'mm',
        initval = 0,
        abslimits = (0, 100),
    ),

    switcher_1 = device('nicos.switcher.Switcher',
                        description = 'switcher',
                        states = ['0', '10', '20', '30', '1000', '-10'],
                        values = [0, 10, 20, 30, 1000, -10],
                        precision = 0,
                        moveable='motor_1'),

    broken_switcher = device('nicos.switcher.Switcher',
                              description = 'broker switcher',
                              states = ['0', '10', '20'],
                              values = [0, 10],
                              precision = 0,
                              moveable='motor_1'),

)
