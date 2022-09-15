description = 'collimation devices'

group = 'lowlevel'

devices = dict(
    ell = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
        visibility = (),
        fmtstr = '%d',
    ),
    col = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
        visibility = (),
        fmtstr = '%d',
    ),
    ellcol = device('nicos_mlz.pgaa.devices.BeamFocus',
        description = 'Switches between focused and collimated Beam',
        ellipse = 'ell',
        collimator = 'col',
        unit = '',
    ),
)

startupcode = """
if ellcol.read() is None:
    ellcol.move('Col')
"""
