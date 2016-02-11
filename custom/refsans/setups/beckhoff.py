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
    # zb0 is at exit of NOK5a (so on its sample side)
    zb0      = device('refsans.beckhoff.nok.BeckhoffMotorCab1M13',
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
    # zb1 is at exit of NOK5b (so on its sample side)
    zb1      = device('refsans.beckhoff.nok.BeckhoffMotorCab1M13',
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

# according to '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
    # det_z is along the scattered beam (inside the tube)
    # beckhoff is at 'detektorantrieb.refsans.frm2' / 172.25.18.108
    table_z = device('refsans.beckhoff.nok.BeckhoffMotorDetector',
                   description = 'table inside tube',
                   tacodevice='//%s/test/modbus/tablee'% (nethost,),
                   address = 0x3020+0*10, # word adress
                   slope = 100,
                   unit = 'mm',
                   # acording to docu:
                   abslimits = (620, 11025),
                  ),
    table_z_obs = device('refsans.beckhoff.nok.BeckhoffCoderDetector',
                       description = 'Coder of detektorantrieb inside tube',
                       tacodevice='//%s/test/modbus/tablee'% (nethost,),
                       address = 0x3020+1*10, # word adress
                       slope = 100,
                       unit = 'mm',
                      ),
# according to '_2013-04-05 Anhang A V0.6.pdf'
    # beckhoff is at 'horizontalblende.refsans.frm2' / 172.25.18.109
    # hs_center is the offset of the slit-center to the beam
    # hs_width is the opening of the slit
    h2_center = device('refsans.beckhoff.nok.BeckhoffMotorHSlit',
                       description = 'Horizontal slit system: offset of the slit-center to the beam',
                       tacodevice='//%s/test/modbus/h2'% (nethost,),
                       address = 0x3020+0*10, # word adress
                       slope = 1000,
                       unit = 'mm',
                       # acording to docu:
                       abslimits = (-69.5, 69.5),
                      ),
    h2_width  = device('refsans.beckhoff.nok.BeckhoffMotorHSlit',
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
    pump_CB      = device('nicos.devices.generic.Switcher',
                          description = 'Pumping state & control device for CB',
                          moveable = device('refsans.beckhoff.pumpstation.PumpstandPump',
                              description = 'pump CB (provided by Pumpstand)',
                              iodev = 'pumpstand',
                              chamber = 'CB',
                             ),
                          precision = 0,
                          mapping = dict(vent=1, off=0, pump=-1),
                         ),
    pump_SR      = device('nicos.devices.generic.Switcher',
                          description = 'Pumping state & control device for SR',
                          moveable = device('refsans.beckhoff.pumpstation.PumpstandPump',
                              description = 'pump SR (provided by Pumpstand)',
                              iodev = 'pumpstand',
                              chamber = 'SR',
                             ),
                          precision = 0,
                          mapping = dict(vent=1, off=0, pump=-1),
                         ),
    pump_SFK     = device('nicos.devices.generic.Switcher',
                          description = 'Pumping state & control device for SFK',
                          moveable = device('refsans.beckhoff.pumpstation.PumpstandPump',
                              description = 'pump SFK (provided by Pumpstand)',
                              iodev = 'pumpstand',
                              chamber = 'SFK',
                             ),
                          precision = 0,
                          mapping = dict(vent=1, off=0, pump=-1),
                         ),
)
