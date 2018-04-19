description = 'NOK5a using Beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

excludes = ['nok5a_old']

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    # NOK5a
    nok5a_r = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5a motor (M11), reactor side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+2*10, # word adresses
        slope = 10000, # FULL steps per turn * turns per mm
        unit = 'mm',
        # acording to docu:
        #abslimits = (0.1, 130),
        abslimits = (-70.0,67.68),
        ruler = 71.0889,
        lowlevel = True,
    ),
    nok5a_s = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5a motor (M12), sample side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+3*10, # word adresses
        slope = 10000, # FULL steps per turn * turns per mm
        unit = 'mm',
        # acording to docu:
        #abslimits = (0.1, 130),
        abslimits = (-79.0,77.85),
        ruler = 79.6439,
        lowlevel = True,
    ),
    # nok5ar_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5a, reactor side',
    #     motor = 'nok5a_r',
    #     coder = 'nok5a_r',
    #     obs = [],
    #     offset = 71.0889,
    #     backlash = 0,
    #     precision = 1000.05,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    # nok5as_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5a, sample side',
    #     motor = 'nok5a_s',
    #     coder = 'nok5a_s',
    #     obs = [],
    #     offset = 79.6439,
    #     backlash = 0,
    #     precision = 1000.002,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    nok5a = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK', #Beckhoff
        description = 'NOK5a',
        fmtstr = '%.2f, %.2f',
        nok_start = 2418.50,
        nok_length = 1719.20,
        nok_end = 4137.70,
        nok_gap = 1.0,
        nok_motor = [3108.00, 3888.00],
        offsets = (0.0, 0.0),  # reactor side, sample side
        inclinationlimits = (-100, 100),   # MP 04.12.2017 12:56:46 by Beckhoff
        motor_r = 'nok5a_r',
        motor_s = 'nok5a_s',
        backlash = -2,   # is this configured somewhere?
        precision = 0.01,
    ),
)
