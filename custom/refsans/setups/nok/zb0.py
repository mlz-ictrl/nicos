description = 'singleSlit [slit k1] between nok5a and nok5b'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    zb0          = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'zb0',
                            nok_start = 4121.5,
                            nok_length = 13.0,
                            nok_end = 4134.5,
                            nok_gap = 1.0,
                            #inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'zb0r',
                            #nok_motor = [3108.0, 3888.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

    zb0r  = device('devices.generic.Axis',
                        description = 'zb0 Reactor side',
                        motor = 'zb0r_m',
                        coder = 'zb0r_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    zb0r_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'zb0r motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+4*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-155.7, -0.2),
                        userlimits = (-155.7, -0.2),
                        #lowlevel = True,
                       ),
)