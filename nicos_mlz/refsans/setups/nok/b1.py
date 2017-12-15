description = 'Slit B1 using Beckhoff controllers'

group = 'lowlevel'

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
    b1_rm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M01), reactorside',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+0*10, # word adress
        slope = 10000,
        unit = 'mm',
        # acording to docu:
        abslimits = (-133, 190),
        userlimits = (-70, 68), # XX: check values!
        lowlevel = True,
    ),
    b1_r = device('nicos.devices.generic.Axis',
        description = 'B1, reactorside',
        motor = 'b1_rm',
        coder = 'b1_rm',
        obs = [],
        offset = 60.0,
        precision = 0.002,
    ),

    # Blendenschild sample side
    # lt. docu bs0_s
    b1_sm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M02), sample side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+1*10, # word adress
        slope = 10000,
        unit = 'mm',
        # acording to docu:
        abslimits = (-152, 120),
        userlimits = (-70, 68), # XX: check values!
        lowlevel = True,
    ),
    b1_s = device('nicos.devices.generic.Axis',
        description = 'B1, sampleside',
        motor = 'b1_sm',
        coder = 'b1_sm',
        obs = [],
        offset = -50.0,
        precision = 0.002,
    ),
)
