description = 'Slit ZB1 using beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    # zb1 is at exit of NOK5b (so on its sample side)
    zb1_m = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M13',
        description = 'CAB1 controlled zb1 (M23), sample side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+7*10, # word adress
        slope = 10000,
        unit = 'mm',
        precision = 0.05,  # precision for a single move
        # acording to docu:
        # abslimits = (-184, -0.1),
        # userlimits = (-146.0656, -0.1),
        # MP 12.12.2017 07:21:50 ruler
        # ruler = -37.9344, #MP 12.12.2017 07:09:29
        ruler = -35.078,  #MP 12.12.2017 07:44:11 #05.05.2017 08:03:07 scan Schaden am Encoder jeden PowerUP neu machen!
        abslimits = (-146.06560000000002, 37.834399999999995),
        userlimits = (-108.13119999999999, 37.834399999999995),
        lowlevel = True,
    ),
    zb1 = device('nicos_mlz.refsans.devices.nok_support.SingleSlit',
        description = 'zb1, singleslit at nok5b before nok6',
        motor = 'zb1_m',
        # coder = 'zb1_m',
        # obs = [],
        offset = 0.0,
        # ruler = -37.9344, # MP 12.12.2017 07:09:29
        precision = 0.05,
        nok_start = 5856.5,
        nok_length = 13,
        nok_end = 5862.5,
        nok_gap = 1,
        nok_motor = 5862.5,
        masks = dict(
            slit = [0, 0],
            point = [0, 0],
            gisans = [-110, 0],
        ),
    ),
    zb1_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'zb1 mode',
        device = 'zb1',
        parameter = 'mode',
    ),
)
