description = 'beckhoff controllers testing'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'

devices = dict(
    # according to 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
    # beckhoff is at 'optic.refsans.frm2' / 172.25.18.115
    # Blendenschild reactor side
    # lt. docu bs0_r
    b1_rm   = device('refsans.beckhoff.nok.BeckhoffMotorCab1M0x',
                     description = 'CAB1 controlled Blendenschild (M01), reactorside',
                     tacodevice='//%s/test/modbus/optic'% (nethost,),
                     address = 0x3020+0*10, # word adress
                     slope = 10000,
                     unit = 'mm',
                     # acording to docu:
                     abslimits = (-133, 190),
                     userlimits = (-70, 68), # XX: check values!
                     lowlevel = True,
                    ),
    b1_r    = device('devices.generic.Axis',
                     description = 'B1, reactorside',
                     motor = 'b1_rm',
                     coder = 'b1_rm',
                     obs = [],
                     offset = 60.0,
                     precision = 0.002,
                    ),

    # Blendenschild sample side
    # lt. docu bs0_s
    b1_sm    = device('refsans.beckhoff.nok.BeckhoffMotorCab1M0x',
                      description = 'CAB1 controlled Blendenschild (M02), sample side',
                      tacodevice='//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+1*10, # word adress
                      slope = 10000,
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (-152, 120),
                      userlimits = (-70, 68), # XX: check values!
                      lowlevel = True,
                     ),
    b1_s    = device('devices.generic.Axis',
                     description = 'B1, sampleside',
                     motor = 'b1_sm',
                     coder = 'b1_sm',
                     obs = [],
                     offset = -50.0,
                     precision = 0.002,
                    ),

    # NOK5a
    nok5a_r  = device('refsans.beckhoff.nok.BeckhoffMotorCab1M11',
                      description = 'nok5a motor (M11), reactor side',
                      tacodevice='//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+2*10, # word adresses
                      slope = 10000, # FULL steps per turn * turns per mm
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (0.1, 130),
                      userlimits = (10, 68), # XX: check values!
                      #lowlevel = True,
                     ),
    nok5a_s  = device('refsans.beckhoff.nok.BeckhoffMotorCab1M12',
                      description = 'nok5a motor (M12), sample side',
                      tacodevice='//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+3*10, # word adresses
                      slope = 10000, # FULL steps per turn * turns per mm
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (0.1, 130),
                      userlimits = (10, 68), # XX: check values!
                      #lowlevel = True,
                     ),
    nok5ar_axis     = device('devices.generic.Axis',
                             description = 'Axis of NOK5a, reactor side',
                             motor = 'nok5a_r',
                             coder = 'nok5a_r',
                             obs = [],
                             offset = 71.0889,
                             backlash = 0,
                             precision = 0.05,
                             unit = 'mm',
                             lowlevel = True,
                            ),
    nok5as_axis     = device('devices.generic.Axis',
                             description = 'Axis of NOK5a, sample side',
                             motor = 'nok5a_s',
                             coder = 'nok5a_s',
                             obs = [],
                             offset = 79.6439,
                             backlash = 0,
                             precision = 0.002,
                             unit = 'mm',
                             lowlevel = True,
                            ),
    nok5a           = device('refsans.nok_support.DoubleMotorNOK',
                             description = 'NOK5a',
                             nok_start = 2418.50,
                             nok_length = 1719.20,
                             nok_end = 4137.70,
                             nok_gap = 1.0,
                             inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                             motor_r = 'nok5ar_axis',
                             motor_s = 'nok5as_axis',
                             nok_motor = [3108.00, 3888.00],
                             backlash = -2,   # is this configured somewhere?
                             precision = 0.002,
                            ),

    # zb0 is at exit of NOK5a (so on its sample side)
    zb0_m    = device('refsans.beckhoff.nok.BeckhoffMotorCab1M13',
                      description = 'CAB1 controlled zb0 (M13), sample side',
                      tacodevice='//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+4*10, # word adress
                      slope = 10000,
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (-184, -0.1),
                      userlimits = (-70, -68), # XX: check values!
                      #lowlevel = True,
                     ),
    zb0     = device('devices.generic.Axis',
                     description = 'zb0, singleslit',
                     motor = 'zb0_m',
                     coder = 'zb0_m',
                     obs = [],
                     offset = -28.2111,
                     precision = 0.002,
                    ),

    # NOK5b
    nok5b_r  = device('refsans.beckhoff.nok.BeckhoffMotorCab1M11',
                      description = 'nok5b motor (M21), reactor side',
                      tacodevice='//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+5*10, # word adresses
                      slope = 10000, # FULL steps per turn * turns per mm
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (0.1, 130),
                      userlimits = (10, 68), # XX: check values!
                      #lowlevel = True,
                     ),
    nok5b_s  = device('refsans.beckhoff.nok.BeckhoffMotorCab1M12',
                      description = 'nok5b motor (M22), sample side',
                      tacodevice='//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+6*10, # word adresses
                      slope = 10000, # FULL steps per turn * turns per mm
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (0.1, 130),
                      userlimits = (10, 68), # XX: check values!
                      #lowlevel = True,
                     ),
    nok5br_axis     = device('devices.generic.Axis',
                             description = 'Axis of NOK5b, reactor side',
                             motor = 'nok5b_r',
                             coder = 'nok5b_r',
                             obs = [],
                             offset = 26.400,
                             backlash = 0,
                             precision = 0.05,
                             unit = 'mm',
                             lowlevel = True,
                            ),
    nok5bs_axis     = device('devices.generic.Axis',
                             description = 'Axis of NOK5b, sample side',
                             motor = 'nok5b_s',
                             coder = 'nok5b_s',
                             obs = [],
                             offset = 43.500,
                             backlash = 0,
                             precision = 0.002,
                             unit = 'mm',
                             lowlevel = True,
                            ),
    nok5b           = device('refsans.nok_support.DoubleMotorNOK',
                             description = 'NOK5b',
                             nok_start = 4153.50,
                             nok_length = 1719.20,
                             nok_end = 5872.70,
                             nok_gap = 1.0,
                             inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                             motor_r = 'nok5br_axis',
                             motor_s = 'nok5bs_axis',
                             nok_motor = [4403.00,5623.00],
                             backlash = -2,   # is this configured somewhere?
                             precision = 0.002,
                            ),
    # zb1 is at exit of NOK5b (so on its sample side)
    zb1_m    = device('refsans.beckhoff.nok.BeckhoffMotorCab1M13',
                      description = 'CAB1 controlled zb1 (M23), sample side',
                      tacodevice='//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+7*10, # word adress
                      slope = 10000,
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (-184, -0.1),
                      userlimits = (-70, -68), # XX: check values!
                      #lowlevel = True,
                     ),
    zb1     = device('devices.generic.Axis',
                     description = 'zb1, singleslit',
                     motor = 'zb1_m',
                     coder = 'zb1_m',
                     obs = [],
                     offset = -37.9344,
                     precision = 0.002,
                    ),

    # according to '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
    # det_z is along the scattered beam (inside the tube)
    # beckhoff is at 'detektorantrieb.refsans.frm2' / 172.25.18.108
    table_z_motor = device('refsans.beckhoff.nok.BeckhoffMotorDetector',
                           description = 'table inside tube',
                           tacodevice='//%s/test/modbus/tablee'% (nethost,),
                           address = 0x3020+0*10, # word adress
                           slope = 100,
                           unit = 'mm',
                           # acording to docu:
                           abslimits = (620, 11025),
                           lowlevel = True,
                          ),
    table_z_obs = device('refsans.beckhoff.nok.BeckhoffCoderDetector',
                         description = 'Coder of detektorantrieb inside tube',
                         tacodevice='//%s/test/modbus/tablee'% (nethost,),
                         address = 0x3020+1*10, # word adress
                         slope = 100,
                         unit = 'mm',
                         lowlevel = True,
                        ),
    table = device('devices.generic.Axis',
                   description = 'table',
                   motor = 'table_z_motor',
                   coder = 'table_z_motor',
                   obs = ['table_z_obs'],
                   precision = 0.05,
                  ),

    # according to '_2013-04-05 Anhang A V0.6.pdf'
    # beckhoff is at 'horizontalblende.refsans.frm2' / 172.25.18.109
    # hs_center is the offset of the slit-center to the beam
    # hs_width is the opening of the slit
    h2_width = device('refsans.beckhoff.nok.BeckhoffMotorHSlit',
                      description = 'Horizontal slit system: offset of the slit-center to the beam',
                      tacodevice='//%s/test/modbus/h2'% (nethost,),
                      address = 0x3020+0*10, # word adress
                      slope = 1000,
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (-69.5, 69.5),
                     ),
    h2_center  = device('refsans.beckhoff.nok.BeckhoffMotorHSlit',
                        description = 'Horizontal slit system: opening of the slit',
                        tacodevice='//%s/test/modbus/h2'% (nethost,),
                        address = 0x3020+1*10, # word adress
                        slope = 1000,
                        unit = 'mm',
                        # acording to docu:
                        abslimits = (0.05, 69.5),
                       ),
    # according to '_Anhang_A_REFSANS_Pumpstand.pdf'
    pumpstand    = device('refsans.beckhoff.pumpstation.PumpstandIO',
                          description = 'io device for pumpstand',
                          tacodevice='//%s/test/modbus/pumpenstand'% (nethost,),
                          address = 0x4026, # 16422
                          parallel_pumping = 10, # below 10mbar, parallel pumping is allowed
                         ),
    pressure_CB  = device('refsans.beckhoff.pumpstation.PumpstandPressure',
                          description = 'Pressure in CB (provided by Pumpstand)',
                          iodev = 'pumpstand',
                          chamber = 'CB',
                          # limits = (turn_pump_off_below_this_pressure, turn_pump_on_above_this_pressure),
                         ),
    pressure_SR  = device('refsans.beckhoff.pumpstation.PumpstandPressure',
                          description = 'Pressure in SR (provided by Pumpstand)',
                          iodev = 'pumpstand',
                          chamber = 'SR',
                          # limits = (turn_pump_off_below_this_pressure, turn_pump_on_above_this_pressure),
                         ),
    pressure_SFK = device('refsans.beckhoff.pumpstation.PumpstandPressure',
                          description = 'Pressure in SFK (provided by Pumpstand)',
                          iodev = 'pumpstand',
                          chamber = 'SFK',
                          # limits = (turn_pump_off_below_this_pressure, turn_pump_on_above_this_pressure),
                         ),
    pump_CB      = device('devices.generic.Switcher',
                          description = 'Pumping state & control device for CB',
                          moveable = device('refsans.beckhoff.pumpstation.PumpstandPump',
                                            description = 'pump CB (provided by Pumpstand)',
                                            iodev = 'pumpstand',
                                            chamber = 'CB',
                                           ),
                          precision = 0.01,
                          mapping = dict(vent=1, off=0, pump=-1),
                         ),
    pump_SR      = device('devices.generic.Switcher',
                          description = 'Pumping state & control device for SR',
                          moveable = device('refsans.beckhoff.pumpstation.PumpstandPump',
                                            description = 'pump SR (provided by Pumpstand)',
                                            iodev = 'pumpstand',
                                            chamber = 'SR',
                                           ),
                          precision = 0.01,
                          mapping = dict(vent=1, off=0, pump=-1),
                         ),
    pump_SFK     = device('devices.generic.Switcher',
                          description = 'Pumping state & control device for SFK',
                          moveable = device('refsans.beckhoff.pumpstation.PumpstandPump',
                                            description = 'pump SFK (provided by Pumpstand)',
                                            iodev = 'pumpstand',
                                            chamber = 'SFK',
                                           ),
                          precision = 0.01,
                          mapping = dict(vent=1, off=0, pump=-1),
                         ),
)
