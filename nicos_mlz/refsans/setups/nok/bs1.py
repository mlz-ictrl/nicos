
description = "DoubleSlit [slit k1] between nok8 and nok9"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    bs1 = device(code_base + 'slits.DoubleSlit',
        description = 'BS1 double between nok8 and nok9',
        fmtstr = 'open: %.3f, zpos: %.3f',
        unit = 'mm',
        slit_r = 'bs1r',
        slit_s = 'bs1s',
    ),
    bs1r = device(code_base + 'slits.SingleSlit',
        # length: 6.0 mm
        description = 'bs1 slit, reactor side',
        motor = 'bs1r_axis',
        nok_start = 9764.5,
        nok_end = 9770.5,
        nok_gap = 18.0,
        masks = {
            'slit': -1.10,  # 2021-03-17 15:37:19 TheoMH -1.725 + _axis -1.8
            'point': 0.70,  # 2021-03-17 15:37:19 TheoMH -1.725
            'gisans': -40.915 * optic_values['gisans_scale'],
        },
        visibility = (),
        unit = 'mm',
    ),
    bs1s = device(code_base + 'slits.SingleSlit',
        # length: 6.0 mm
        description = 'bs1 slit, sample side',
        motor = 'bs1s_axis',
        nok_start = 9764.5,
        nok_end = 9770.5,
        nok_gap = 18.0,
        masks = {
            'slit': -1.00,  # 2021-03-17 15:37:19 TheoMH -2.255
            'point': -1.00,  # 2021-03-17 15:37:19 TheoMH -2.255
            'gisans':-2.255,
        },
        visibility = (),
        unit = 'mm',
    ),
    bs1r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of BS1, reactor side',
        motor = 'bs1r_motor',
        # obs = ['bs1r_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    bs1r_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'bs1r_motor',
         device2 = 'bs1r_analog',
         visibility = showcase_values['hide_acc'],
    ),
    bs1r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for BS1, reactor side',
        reference = 'nok_refc2',
        measure = 'bs1r_poti',
        # 2020-04-20 17:33:56 poly = [-108.4, 998.068 / 3.835],
        # 2020-04-21 07:59:00 poly = [-106.429, 998.068 / 3.835],
        poly = [-105.176, 998.068 / 3.835],
        serial = 7542,
        length = 250.0,
        visibility = showcase_values['hide_poti'] & showcase_values['NOreference'],
    ),
    bs1r_poti = device(code_base + 'nok_sensor.NOKMonitoredVoltage',
        description = 'Poti for BS1, reactor side',
        tangodevice = tango_base + 'test/wb_c/2_1',
        scale = 1,   # mounted from bottom
        visibility = (),
    ),
    bs1s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of BS1, sample side',
        motor = 'bs1s_motor',
        # obs = ['bs1s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    bs1s_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'bs1s_motor',
         device2 = 'bs1s_analog',
         visibility = showcase_values['hide_acc'],
    ),
    bs1s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for BS1, sample side',
        reference = 'nok_refc2',
        measure = 'bs1s_poti',
        # 2020-04-29 11:56:21 poly = [39.1, 999.452 / 1.919],
        poly = [39.1, 999.452 / 1.919],
        serial = 7784,
        length = 500.0,
        visibility = showcase_values['hide_poti'] & showcase_values['NOreference'],
    ),
    bs1s_poti = device(code_base + 'nok_sensor.NOKMonitoredVoltage',
        description = 'Poti for BS1, sample side',
        tangodevice = tango_base + 'test/wb_c/2_5',
        scale = 1,   # mounted from bottom
        visibility = (),
    ),
)

alias_config = {
    'primary_aperture': {'bs1.opening': 200},
}
