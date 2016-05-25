description = 'doubleSlit [slit] between nok4 and nok5a'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    b1          = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'b1',
                            optic_start = 2374.0,
                            optic_length = 13.5,
                            optic_end = 2387.5,
                            optic_gap = 0,
                            #inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'b1r',
                            motor_s = 'b1s',
                            #nok_motor = [3108.0, 3888.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

    b1r  = device('devices.generic.Axis',
                        description = 'b1 Reactor side',
                        motor = 'b1r_m',
                        coder = 'b1r_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    b1r_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'b1r motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+0*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-133, 130),
                        userlimits = (-133, 130),
                        #lowlevel = True,
                       ),

    b1s  = device('devices.generic.Axis',
                        description = 'b1 Sample side',
                        motor = 'b1s_m',
                        coder = 'b1s_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    b1s_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'b1s motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+1*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-102, 120),
                        userlimits = (-102, 120),
                        #lowlevel = True,
                       ),
)
