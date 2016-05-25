description = 'neutronguid sideMirror noMirror polarisator'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    h2          = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'h2',
                            inclinationlimits = (-100, 100),   # invented values, PLEASE CHECK!
                            motor_r = 'h2o',
                            motor_s = 'h2l',
                            #nok_motor = [3108.0, 3888.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

    h2o  = device('devices.generic.Axis',
                        description = 'h2 open',
                        motor = 'h2o_m',
                        coder = 'h2o_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    h2o_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'h2 open motor',
                        tacodevice='//%s/test/modbus/h2'% (nethost,),
                        address = 0x3020+1*10, # word adresses
                        slope = 1000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (.8, 80),
                        userlimits = (.8, 80),
                        #lowlevel = True,
                       ),

    h2l  = device('devices.generic.Axis',
                        description = 'h2 lateral',
                        motor = 'h2l_m',
                        coder = 'h2l_m',
                        dragerror = 1,
                        precision = 0.1,
                        jitter = 0.1,
                       ),
    h2l_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'h2 lateral motor',
                        tacodevice='//%s/test/modbus/h2'% (nethost,),
                        address = 0x3020+0*10, # word adresses
                        slope = 1000, # FULL steps per turn * turns per mm
                        unit = 'mm',
                        abslimits = (-50, 50),
                        userlimits = (-50, 50),
                        #lowlevel = True,
                       ),
)
