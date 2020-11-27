description = 'sample table and radial collimator'

group = 'lowlevel'

tango_base = 'tango://tofhw.toftof.frm2.tum.de:10000/toftof/hubermc/'

devices = dict(
    gx = device('nicos.devices.tango.Motor',
        description = 'X translation of the sample table',
        tangodevice = tango_base + 'gxm',
        fmtstr = '%7.3f',
        # abslimits = (0.0, 40.),
    ),
    gy = device('nicos.devices.tango.Motor',
        description = 'Y translation of the sample table',
        tangodevice = tango_base + 'gym',
        fmtstr = '%7.3f',
        # abslimits = (0.0, 40.),
    ),
    gz = device('nicos.devices.tango.Motor',
        description = 'Z translation of the sample table',
        tangodevice = tango_base + 'gzm',
        fmtstr = '%7.3f',
        # abslimits = (-14.8, 50.),
    ),
    gcx = device('nicos.devices.tango.Motor',
        description = 'Chi rotation of the sample goniometer',
        tangodevice = tango_base + 'gcxm',
        fmtstr = '%7.3f',
        # abslimits = (-20.0, 20.),
    ),
    gcy = device('nicos.devices.tango.Motor',
        description = 'Psi rotation of the sample goniometer',
        tangodevice = tango_base + 'gcym',
        fmtstr = '%7.3f',
        # abslimits = (-20.0, 20.),
    ),
    gphi = device('nicos.devices.tango.Motor',
        description = 'Phi rotation of the sample table',
        tangodevice = tango_base + 'gphim',
        fmtstr = '%7.3f',
        # abslimits = (-100.0, 100.),
    ),
)
