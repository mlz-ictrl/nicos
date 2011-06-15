name = 'test slit'
includes = ['system']


devices = dict(

    motor_left = device('nicos.virtual.VirtualMotor',
                        unit = 'mm',
                        abslimits= (-10, 20)),

    motor_right = device('nicos.virtual.VirtualMotor',
                        unit = 'mm',
                        abslimits= (-20, 10)),

    motor_bottom = device('nicos.virtual.VirtualMotor',
                          unit = 'mm',
                          abslimits= (-20, 10)),

    motor_top = device('nicos.virtual.VirtualMotor',
                       unit = 'mm',
                       abslimits= (-10, 20)),


    slit_1 = device('nicos.slit.Slit',
                    left = 'motor_left',
                    right = 'motor_right',
                    bottom = 'motor_bottom',
                    top = 'motor_top',
                    pollinterval = 5,
                    maxage = 10),
)
