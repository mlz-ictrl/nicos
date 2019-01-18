description = 'Slit ZB0 using Beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
global_values = configdata('global.GLOBAL_Values')

devices = dict(
    zb0_m = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M13',
        description = 'CAB1 controlled zb0 (M13), sample side',
        tacodevice = '//%s/test/modbus/optic' % (nethost,),
        address = 0x3020+4*10, # word address
        slope = 10000,
        unit = 'mm',
        ruler = -28.2111,
        abslimits = (-155.7889, 28.111099999999997),
        lowlevel = True,
    ),
    zb0_a = device('nicos.devices.generic.Axis',
        description = 'zb0 axis',
        motor = 'zb0_m',
        precision = global_values['precision'],
        maxtries = 3,
        lowlevel = True,
    ),
    zb0 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'zb0, singleslit',
        motor = 'zb0_a',
        nok_start = 4121.5,
        nok_length = 13,
        nok_end = 4134.5,
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -110,
        },
        unit = 'mm',
    ),
    zb0_temp = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffTemp',
        description = 'Temperatur for ZB0 Motor',
        tacodevice = '//%s/test/modbus/optic'% (nethost,),
        address = 0x3020+4*10, # word address
        abslimits = (-1000, 1000),
        lowlevel = global_values['hide_poti'],
    ),
    zb0_obs = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffPoti',
        description = 'Poti for ZB0 no ref',
        tacodevice = '//%s/test/modbus/optic' % (nethost,),
        address = 0x3020+4*10, # word address
        abslimits = (-1000, 1000),
        poly = [-176.49512271969755, 0.00794154091586989],
        lowlevel = global_values['hide_poti'],
    ),
    zb0_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb0_m',
         analog = 'zb0_obs',
         lowlevel = global_values['hide_acc'],
         unit = 'mm'
    ),
    zb0_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'zb0 mode',
        device = 'zb0',
        parameter = 'mode',
    ),
)
