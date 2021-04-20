description = "SingleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts']

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
        lowlevel = True,
    ),
    zb2_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for ZB2',
        reference = 'nok_refb2',
        measure = 'zb2_poti',
        poly = [-116.898256, 999.872 / 1.921],
        serial = 7786,
        length = 500.0,
        lowlevel = showcase_values['hide_poti'],
    ),
    zb2_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb2_motor',
         analog = 'zb2_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),
    zb2_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for ZB2',
        tangodevice = tango_base + 'test/wb_b/2_3',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
)
