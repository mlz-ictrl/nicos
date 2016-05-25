description = 'singleSlit [slit k1] between nok5b and nok6'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    zb1          = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'zb1',
                            nok_start = 5856.5,
                            nok_length = 13.0,
                            nok_end = 5869.5,
                            nok_gap = 1.0,
                            #inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'zb1r',
                            #nok_motor = [3108.0, 3888.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

    zb1r  = device('devices.generic.Axis',
                        description = 'zb1 Reactor side',
                        motor = 'zb1r_m',
                        coder = 'zb1r_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    zb1r_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'zb1r motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+7*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-152.1, -0.2),
                        userlimits = (-152.1, -0.2),
                        #lowlevel = True,
                       ),
)