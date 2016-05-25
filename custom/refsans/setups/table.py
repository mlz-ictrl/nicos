description = 'distance Detektor Pivot'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    table          = device('devices.generic.Axis',
                            description = 'table',
                            motor = 'table_m',
                            coder = 'table_m',
                            precision = 0.05,
                           ),
    table_m  = device('refsans.beckhoff.BeckhoffMotor',
                        description = 'tabler motor',
                        tacodevice='//%s/test/modbus/tablee'% (nethost,),
                        address = 0x3020+0*10, # word adresses
                        slope = 100000, # FULL steps per turn * turns per mm
                        unit = 'm',
                        abslimits = (.8, 11.025),
                        userlimits = (.8, 11.025),
                        #lowlevel = True,
                       ),
)