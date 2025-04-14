
description = "DoubleSlit [slit k1] between nok8 and nok9"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts', 'weg03']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    bs1 = device(code_base + 'slits.DoubleSlit',
        description = 'BS1 double between nok8 and nok9',
        fmtstr = 'zpos: %.3f, open: %.3f',
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
)

alias_config = {
    'primary_aperture': {'bs1.opening': 200},
}
