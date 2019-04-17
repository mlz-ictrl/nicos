description = 'autocollimator, water subtracted, vendor Trioptic'

group = 'lowlevel'

all_lowlevel = False  # or True

tango_host = 'tango://refsanshw.refsans.frm2:10000/test/triangle/io'

devices = dict(
    autocollimator = device('nicos_mlz.refsans.devices.triangle.TriangleMaster',
        description = description,
        tangodevice = tango_host,
        lowlevel = True,  # all_lowlevel,
        unit = '',
    ),
    autocollimator_theta = device('nicos_mlz.refsans.devices.triangle.TriangleAngle',
        description = description + ', autocollimator Y on PC',
        lowlevel = all_lowlevel,
        index = 0,
        tangodevice = tango_host,
        scale = 1,
        unit = 'deg',
    ),
    autocollimator_phi = device('nicos_mlz.refsans.devices.triangle.TriangleAngle',
        description = description + ', autocollimator X on PC',
        lowlevel = all_lowlevel,
        index = 1,
        tangodevice = tango_host,
        scale = -1,
        unit = 'deg',
    ),
)
