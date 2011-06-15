name = 'test switcher'

includes = ['system']

devices = dict(

    motor_1 = device(
        'nicos.virtual.VirtualMotor',
        unit = 'mm',
        initval = 0,
        abslimits = (0, 100),
    ),

    switch = device('nicos.switcher.Switcher',
                    description = 'switch',
                    states = ['0', '10', '20', '30', '1000'],
                    values = [0, 10, 20, 30, 1000],
                    precision = 0,
                    moveable='motor_1'),

)
