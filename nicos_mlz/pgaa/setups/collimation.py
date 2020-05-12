description = 'collimation devices'

group = 'lowlevel'

tango_base = 'tango://pgaahw.pgaa.frm2.tum.de:10000/pgaa/sample/'

devices = dict(
    ell = device('nicos.devices.tango.DigitalOutput',
        description = '',
        tangodevice = tango_base + 'elcol_press1',
        lowlevel = True,
        fmtstr = '%d',
    ),
    col = device('nicos.devices.tango.DigitalOutput',
        description = '',
        tangodevice = tango_base + 'elcol_press2',
        lowlevel = True,
        fmtstr = '%d',
    ),
    ellcol = device('nicos_mlz.pgaa.devices.BeamFocus',
        description = 'Switches between focused and collimated Beam',
        ellipse = 'ell',
        collimator = 'col',
        unit = ''
    ),
)
