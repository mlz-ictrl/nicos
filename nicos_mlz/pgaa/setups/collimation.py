description = 'collimation devices'

group = 'lowlevel'

includes = []

nethost = 'pgaasrv.pgaa.frm2'

devices = dict(
    ell = device('nicos.devices.taco.io.DigitalOutput',
        description = '',
        tacodevice = '//pgaasrv/pgaa/sample/elcol_press1',
        lowlevel = True
    ),
    col = device('nicos.devices.taco.io.DigitalOutput',
        description = '',
        tacodevice = '//pgaasrv/pgaa/sample/elcol_press2',
        lowlevel = True
    ),
    ellcol = device('nicos_mlz.pgaa.devices.BeamFocus',
        description = 'Switches between focused and collimated Beam',
        ellipse = 'ell',
        collimator = 'col',
    ),
)
