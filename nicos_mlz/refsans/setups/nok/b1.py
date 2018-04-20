description = 'Slit B1 using Beckhoff controllers'

group = 'lowlevel'
nethost = 'refsanssrv.refsans.frm2'
global_values = configdata('global.GLOBAL_Values')
lprecision = 0.005 # global_values['precision']

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    b1 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'b1 end of Chopperburg',
        fmtstr = 'opening: %.3f mm, zpos: %.3f mm',
        slit_r = 'b1r',
        slit_s = 'b1s',
        unit = '',
    ),
    b1r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'b1 slit, reactor side',
        motor = 'b1_r',
        masks = {
            'slit':   0.0, #3.5699,  # 0,
            'point':  3.5699,  # 0,
            'gisans': 3.5699,  # 0,
        },
        nok_start = 2374.0,
        nok_length = 13.5,
        # nok_motor = [2380.0, 2387.5],
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        lowlevel = True,
    ),
    b1s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'xxx slit, sample side',
        motor = 'b1_s',
        masks = {
            'slit':   0.0, #3.73,  # 0,
            'point':  3.73,  # 0,
            'gisans': 3.73,  # 0,
        },
        nok_start = 2374.0,
        nok_length = 13.5,
        # nok_motor = [2380.0, 2387.5],
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        lowlevel = True,
    ),
    b1_r = device('nicos.devices.generic.Axis',
        description = 'B1, reactorside',
        motor = 'b1_rm',
        # offset = 60.0,
        offset = 0.0,
        precision = lprecision,
        maxtries = 3,
        lowlevel = True,
    ),
    b1_s = device('nicos.devices.generic.Axis',
        description = 'B1, sampleside',
        motor = 'b1_sm',
        # offset = -50.0,
        offset = 0.0,
        precision = lprecision,
        maxtries = 3,
        lowlevel = True,
    ),
    # according to 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
    # beckhoff is at 'optic.refsans.frm2' / 172.25.18.115
    b1_rm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M01), reactorside',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+0*10, # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-133, 190), # XX: check values!
        ruler = 60.0,
        lowlevel = True,
    ),
    b1_sm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M02), sample side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+1*10, # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-152, 120), # XX: check values!
        ruler = -50.0,
        lowlevel = True,
    ),
)
