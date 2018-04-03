description = 'Trioptic autocollimator, water subtracted'

# not included by others
group = 'optional'

all_lowlevel = False  # or True

tango_host = 'tango://refsanshw.refsans.frm2:10000/test/triangle/io'

devices = dict(
    triangle = device('nicos_mlz.refsans.devices.triangle.TriangleMaster',
        description = description,
        tangodevice = tango_host,
        lowlevel = True,  # all_lowlevel,
        unit = '',
    ),
    triangle_theta = device('nicos_mlz.refsans.devices.triangle.TriangleAngle',
        description = description + ', triangle Y on PC',
        lowlevel = all_lowlevel,
        index = 0,
        tangodevice = tango_host,
        unit = '',
    ),
    triangle_phi = device('nicos_mlz.refsans.devices.triangle.TriangleAngle',
        description = description + ', triangle X on PC',
        lowlevel = all_lowlevel,
        index = 1,
        tangodevice = tango_host,
        unit = '',
    ),
)
