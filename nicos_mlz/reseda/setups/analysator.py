description = 'Analyser rotation'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2.tum.de:10000/reseda'

devices = dict(
    analysator_rot = device('nicos.devices.entangle.Motor',
        description = 'Rotation analyzer (motor)',
        tangodevice = '%s/hupp/mot12' % tango_base,
        fmtstr = '%.3f',
        unit = 'deg'
        # abslimits = (-5.0, 60.0)
    ),
)
