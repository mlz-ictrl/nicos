description = "DoubleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

devices = dict(
    zb3 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'ZB3 slit',
        slit_r = 'zb3r',
        slit_s = 'zb3s',
        fmtstr = 'opening: %.3f mm, zpos: %.3f mm',
        unit = '',
    ),
    zb3r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.0 mm
        description = 'ZB3 slit, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-221.0, 95.0),
            unit = 'mm',
            speed = 1.,
        ),
        nok_start = 8856.5, # 8837.5,
        nok_end = 8869.5, # 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': -0.3,
            'point': 0,
            'gisans': -110,
        },
        unit = 'mm',
        lowlevel = True,
    ),
    zb3s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13.0 mm
        description = 'ZB3 slit, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-106.0, 113.562),
            unit = 'mm',
            speed = 1.,
        ),
        nok_start = 8856.5, # 8837.5,
        nok_end = 8869.5, # 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': 1.7,
            'point': 0,
            'gisans': 0,
        },
        unit = 'mm',
        lowlevel = True,
    ),
)

alias_config = {
    'primary_aperture': {'zb3': 100},
}
