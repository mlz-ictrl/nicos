description = 'Manual devices for setting camera meta data that can not be captured automatically'

devices = dict(
    scintillator = device('nicos_sinq.imaging.devices.misc.ManualSettableSwitch',
        description = 'Scintillator installed in the camera box',
        states = ['other'],
    ),
    lens = device('nicos_sinq.imaging.devices.misc.ManualSettableSwitch',
        description = 'Lens installed in the camera box',
        states = ['other'],
    ),
    pixelsize = device('nicos.devices.generic.manual.ManualMove',
        description = 'Effective pixel size',
        abslimits = (0, 1E6),
        unit = 'um',
        fmtstr = '%.2f',
    ),
    fov = device('nicos.devices.generic.manual.ManualMove',
        description = 'Field of view, number of camera pixels in x and y times pixel size',
        abslimits = (0, 1E10),
        unit = 'mm',
        fmtstr = '%.2f',
    ),
)
