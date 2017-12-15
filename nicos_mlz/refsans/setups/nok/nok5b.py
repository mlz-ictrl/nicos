description = 'NOK5b using Beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

excludes = ['nok5b_old']

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    # NOK5b
    nok5b_r = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5b motor (M21), reactor side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+5*10, # word adresses
        slope = 10000, # FULL steps per turn * turns per mm
        unit = 'mm',
        # acording to docu:
        abslimits = (0.1, 130),
        userlimits = (10, 68), # XX: check values!
        #lowlevel = True,
    ),
    nok5b_s = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5b motor (M22), sample side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+6*10, # word adresses
        slope = 10000, # FULL steps per turn * turns per mm
        unit = 'mm',
        # acording to docu:
        abslimits = (0.1, 130),
        userlimits = (10, 68), # XX: check values!
        #lowlevel = True,
    ),
    # nok5br_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5b, reactor side',
    #     motor = 'nok5b_r',
    #     coder = 'nok5b_r',
    #     obs = [],
    #     offset = 26.400,
    #     backlash = 0,
    #     precision = 0.05,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    # nok5bs_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5b, sample side',
    #     motor = 'nok5b_s',
    #     coder = 'nok5b_s',
    #     obs = [],
    #     offset = 43.500,
    #     backlash = 0,
    #     precision = 0.002,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    nok5b = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOKBeckhoff',
        description = 'NOK5b',
        nok_start = 4153.50,
        nok_length = 1719.20,
        nok_end = 5872.70,
        nok_gap = 1.0,
        offsets = (26.400,43.500,),      # reactor side, sample side
        inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
        motor_r = 'nok5b_r',
        motor_s = 'nok5b_s',
        nok_motor = [4403.00,5623.00],
        backlash = -2,   # is this configured somewhere?
        precision = 0.002,
    ),
)
