description = 'neutronguid sideMirror noMirror Spinflipper'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok5b          = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK5B',
                            nok_start = 4153.5,
                            nok_length = 1720.0,
                            nok_end = 5873.5,
                            nok_gap = 1.0,
                            #inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok5br',
                            motor_s = 'nok5bs',
                            #nok_motor = [3108.0, 3888.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

    nok5br  = device('devices.generic.Axis',
                        description = 'NOK5b Reactor side',
                        motor = 'nok5br_m',
                        coder = 'nok5br_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    nok5br_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'nok5b Reaktorside motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+5*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-26, 86),
                        userlimits = (-26, 86),
                        #lowlevel = True,
                       ),

    nok5bs  = device('devices.generic.Axis',
                        description = 'NOK5b Sample side',
                        motor = 'nok5bs_m',
                        coder = 'nok5bs_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    nok5bs_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'nok5bs motor',
                        tacodevice='//%s/test/modbus/optic'% (nethost,),
                        address = 0x3020+6*10, # word adresses
                        slope = 10000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-43, 98),
                        userlimits = (-43, 98),
                        #lowlevel = True,
                       ),
)
