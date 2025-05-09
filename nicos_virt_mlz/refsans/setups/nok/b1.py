description = 'Slit B1 using Beckhoff controllers'

group = 'lowlevel'

lprecision = 0.005

devices = dict(
    b1 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'b1 end of Chopperburg',
        fmtstr = 'opening: %.3f mm, zpos: %.3f mm',
        slit_r = 'b1r',
        slit_s = 'b1s',
        unit = '',
    ),
    b1r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.5 mm
        description = 'b1 slit, reactor side',
        motor = 'b1_r',
        masks = {
            'slit':   0.0,
            'point':  3.5699,
            'gisans': 3.5699,
        },
        nok_start = 2374.0,
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        visibility = (),
    ),
    b1s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.5 mm
        description = 'b1 slit, sample side',
        motor = 'b1_s',
        masks = {
            'slit':   0.0,
            'point':  3.73,
            'gisans': 3.73,
        },
        nok_start = 2374.0,
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        visibility = (),
    ),
    b1_r = device('nicos.devices.generic.Axis',
        description = 'B1, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-133, 127),
            speed = 1.,
        ),
        offset = 0.0,
        precision = lprecision,
        maxtries = 3,
        visibility = (),
    ),
    b1_s = device('nicos.devices.generic.Axis',
        description = 'B1, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-102, 170),
            speed = 1.,
        ),
        offset = 0.0,
        precision = lprecision,
        maxtries = 3,
        visibility = (),
    ),
)

alias_config = {
    'primary_aperture': {'b1.opening': 100},
}
