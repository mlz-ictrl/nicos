description = 'neutronguid sideMirror noMirror polarisator'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok5a          = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK5A',
                            nok_start = 2418.5,
                            nok_length = 1720.0,
                            nok_end = 4138.5,
                            nok_gap = 1.0,
                            #inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok5ar',
                            motor_s = 'nok5as',
                            #nok_motor = [3108.0, 3888.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

    nok5ar  = device('devices.generic.Axis',
                        description = 'NOK5a Reactor side',
                        motor = 'nok5ar_m',
                        coder = 'nok5ar_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    nok5ar_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'nok5ar motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+2*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-70, 68),
                        userlimits = (-70, 68),
                        #lowlevel = True,
                       ),

    nok5as  = device('devices.generic.Axis',
                        description = 'NOK5a Sample side',
                        motor = 'nok5as_m',
                        coder = 'nok5as_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    nok5as_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'nok5as motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+3*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-79, 78),
                        userlimits = (-79, 78),
                        #lowlevel = True,
                       ),
)
