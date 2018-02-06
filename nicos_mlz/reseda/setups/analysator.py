#  -*- coding: utf-8 -*-

description = 'Analyser rotation'
group = 'optional'

taco_base = '//resedasrv.reseda.frm2/reseda'
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    analysator_rot = device('nicos.devices.tango.Motor',
        description = 'Rotation analyer (motor)',
        tangodevice = '%s/hupp/mot12' % tango_base,
        fmtstr = '%.3f',
        unit = 'deg'
        # abslimits = (-5.0, 60.0)
    ),
)
