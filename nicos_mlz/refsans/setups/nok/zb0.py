description = 'Slit ZB0 using Beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    # zb0 is at exit of NOK5a (so on its sample side)
    zb0_m = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M13',
        description = 'CAB1 controlled zb0 (M13), sample side',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+4*10, # word adress
        slope = 10000,
        unit = 'mm',
        precision = 0.05,  # precision for a single move
        # acording to docu:
        # abslimits = (-184, -0.1),
        # userlimits = (-155.7889, -0.1),
        # MP 12.12.2017 07:01:32 - ruler -28.2111 bzw offset
        ruler = -28.2111,
        abslimits = (-155.7889, 28.111099999999997),
        userlimits = (-127.57780000000001, 28.111099999999997),
        lowlevel = True,
    ),
    zb0 = device('nicos_mlz.refsans.devices.nok_support.SingleSlit',
        description = 'zb0, singleslit at nok5a before nok5b',
        motor = 'zb0_m',
        # coder = 'zb0_m',
        # obs = [],
        # offset = -28.2111,
        offset = 0.0,
        # ruler = -28.2111,
        precision = 0.05,  # precision after repositionings
        nok_start   = 4121.5,
        nok_length  = 13,
        nok_end     = 4134.5,
        nok_gap     = 1,
        nok_motor   = 4128.5,
        masks = dict(
            slit = [0, 0],
            point = [0, 0],
            gisans = [-110, 0],
        ),
    ),
    zb0_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'zb0 mode',
        device = 'zb0',
        parameter = 'mode',
    ),
)
