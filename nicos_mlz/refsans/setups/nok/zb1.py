description = 'Slit ZB1 using beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
showcase_values = configdata('cf_showcase.showcase_values')

devices = dict(
    zb1 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'zb1, singleslit at nok5b before nok6',
        unit = 'mm',
        motor = 'zb1_m',
        offset = 0.0,
        nok_start = 5856.5,
        nok_length = 13,
        nok_end = 5862.5,
        nok_gap = 1,
        # nok_motor = 5862.5,
        masks = {
            'slit':    0,
            'point':   0,
            'gisans':  -110,
        },
    ),
    zb1_a = device('nicos.devices.generic.Axis',
        description = 'zb1 axis',
        motor = 'zb1_m',
        precision = 0.02,
        maxtries = 3,
        lowlevel = True,
    ),
    zb1_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'zb1 mode',
        device = 'zb1',
        parameter = 'mode',
    ),
    zb1_m = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M13',
        description = 'CAB1 controlled zb1 (M23), sample side',
        tacodevice = '//%s/test/modbus/optic' % (nethost,),
        address = 0x3020+7*10, # word address
        slope = 10000,
        unit = 'mm',
        ruler = -54.080,
        abslimits = (-178.9,  53.9),
        lowlevel = True,
    ),
    zb1_obs = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffPoti',
        description = 'Poti for ZB1 no ref',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+7*10, # word address
        abslimits = (-1000, 1000),
        poly =  [-283.16351478707793, 0.015860537603265893],
        lowlevel = True or showcase_values['hide_poti'],
    ),
    zb1_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb1_m',
         analog = 'zb1_obs',
         lowlevel = True or showcase_values['hide_acc'],
         unit = 'mm'
    ),
)
