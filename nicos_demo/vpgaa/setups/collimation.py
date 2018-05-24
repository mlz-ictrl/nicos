description = 'collimation devices'

group = 'lowlevel'

devices = dict(
    ell = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
        lowlevel = True,
    ),
    col = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
        lowlevel = True,
    ),
    ellcol = device('nicos_mlz.pgaa.devices.BeamFocus',
        description = 'Switches between focused and collimated Beam',
        ellipse = 'ell',
        collimator = 'col',
        unit = '',
    ),
)
