description = "SingleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']
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
        motor = 'zb2_motor',
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
    zb2_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of ZB2',
        abslimits = (-215.69, 93.0),
        bus = 'nokbus1',
        addr = 0x37,
        slope = 800.0,
        speed = 50,
        accel = 50,
        confbyte = 32,
        ramptype = 2,
        microstep = 1,
        refpos = 68.0465,
        zerosteps = int(681.95 * 800),
        lowlevel = showcase_values['hide_poti'],
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
