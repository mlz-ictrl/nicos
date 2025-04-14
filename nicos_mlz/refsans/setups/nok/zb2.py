description = "SingleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts', 'weg02']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']
optic_values = configdata('cf_optic.optic_values')

devices = dict(
    zb2 = device(code_base + 'slits.SingleSlit',
        # length: 6.0,
        description = 'zb2 single Slit at nok6 before nok7',
        unit = 'mm',
        motor = 'zb2_axis',
        nok_start = 7633.5, # 7591.5
        nok_end = 7639.5, # 7597.5
        nok_gap = 1.0,
        offset = 0.0,
        masks = {
            'slit':     -2,
            'point':   -2,
            'gisans':    -122.0 * optic_values['gisans_scale'],
        },
    ),
    zb2_axis = device('nicos.devices.generic.Axis',
        description = 'zb2 single Slit for backlash',
        motor = 'zb2_motor',
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    zb2_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'zb2_motor',
         device2 = 'zb2_analog',
         visibility = showcase_values['hide_acc'],
    ),
)
