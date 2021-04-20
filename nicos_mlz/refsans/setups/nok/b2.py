description = 'at samplecamper [slit k1]'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']
optic_values = configdata('cf_optic.optic_values')

devices = dict(
    #
    ## smccorvusserver b2 exports
    #
    b2 = device(code_base + 'slits.DoubleSlit',
        description = 'b2 at sample pos',
        fmtstr = 'opening: %.3f mm, zpos: %.3f mm',
        unit = '',
        slit_r = 'b2r',
        slit_s = 'b2s',
    ),
    b2r = device(code_base + 'slits.SingleSlit',
        # length: 13.0 mm
        description = 'b2 slit, reactor side; 220 full access, 74 for upper srcews',
        motor = 'b2r_motor',
        nok_start = 11049.50,
        nok_end = 11064.50,
        nok_gap = 1.0,
        masks = {
            'slit': 0.225,  # 2021-03-17 16:13:48 TheoMH 0.0
            'point': 0.225,  # 2021-03-17 16:13:48 TheoMH 0.0
            'gisans': 0.225,  # 2021-03-17 16:13:48 TheoMH 0.0
        },
        lowlevel = True,
        unit = 'mm',
    ),
    b2s = device(code_base + 'slits.SingleSlit',
        # length: 13.0 mm
        description = 'b2 slit, sample side; -291 full access, -182 low row',
        motor = 'b2s_motor',
        nok_start = 11049.50,
        nok_end = 11064.50,
        nok_gap = 1.0,
        masks = {
            'slit': -1.225,  # 2021-03-17 16:13:48 TheoMH 0.0
            'point': -1.225,  # 2021-03-17 16:13:48 TheoMH 0.0
            'gisans': -85 * optic_values['gisans_scale'],
        },
        unit = 'mm',
        lowlevel = True,
    ),
    # b2_r = device('nicos.devices.generic.Axis',
    #     description = 'b2, reactorside',
    #     motor = 'smccorvus_b2mr',
    #     backlash = 0,
    #     precision = 0.02,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    # b2_s = device('nicos.devices.generic.Axis',
    #     description = 'b2, sampleside',
    #     motor = 'smccorvus_b2ms',
    #     backlash = 0,
    #     precision = 0.02,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    b2r_motor = device('nicos.devices.tango.Motor',
        description = 'b2 reactor side, screw access at 72mm',
        tangodevice = tango_base + 'test/smccorvus/b2mr',
        userlimits = (-288, 227),
        lowlevel = True,
    ),
    b2s_motor = device('nicos.devices.tango.Motor',
        description = 'b2 sample side',
        tangodevice = tango_base + 'test/smccorvus/b2ms',
        userlimits = (-291, 224),
        lowlevel = True,
    ),
)

alias_config = {
    'last_aperture': {'b2.height': 100},
}
