description = 'at samplecamper [slit k1]'

group = 'lowlevel'

devices = dict(
    b2 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'b2 at sample pos',
        fmtstr = 'opening: %.3f mm, zpos: %.3f mm',
        unit = '',
        slit_r = 'b2r',
        slit_s = 'b2s',
    ),
    b2r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.0 mm
        description = 'b2 slit, reactor side; 220 full access, 74 for upper srcews',
        motor = 'b2_r',
        nok_start = 11049.50,
        nok_end = 11064.50,
        nok_gap = 1.0,
        masks = {
            'slit':   0.0,
            'point':  -4.067,
            'gisans': -218.645,
        },
        visibility = (),
        unit = 'mm',
    ),
    b2s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.0 mm
        description = 'b2 slit, sample side; -291 full access, -182 low row',
        motor = 'b2_s',
        nok_start = 11049.50,
        nok_end = 11064.50,
        nok_gap = 1.0,
        masks = {
            'slit':   0.0,
            'point':  -0.233,
            'gisans': 206.4,
        },
        unit = 'mm',
        visibility = (),
    ),
    b2_r = device('nicos.devices.generic.Axis',
        description = 'b2, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-1294, 1222),
            speed = 3.,
            unit = 'mm',
        ),
        backlash = 0,
        precision = 0.02,
        visibility = (),
    ),
    b2_s = device('nicos.devices.generic.Axis',
        description = 'b2, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-2960, 2130),
            speed = 3.,
            unit = 'mm',
        ),
        backlash = 0,
        precision = 0.02,
        visibility = (),
    ),
)

alias_config = {
    'last_aperture': {'b2.opening': 100},
}
