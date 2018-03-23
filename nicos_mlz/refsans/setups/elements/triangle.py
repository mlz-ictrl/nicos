description = 'Trioptic autocollimator'

# not included by others
group = 'optional'

all_lowlevel = False  # or True

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    triangle = device('nicos_mlz.refsans.devices.triangle.TriangleMaster',
        description = description,
        tacodevice = '//%s/test/network/triangle' % nethost,
        lowlevel = all_lowlevel,
    ),
    triangle_theta = device('nicos_mlz.refsans.devices.triangle.TriangleAngle',
        description = 'triangle_Y',
        lowlevel = all_lowlevel,
        index = 0,
        tacodevice = '//%s/test/network/triangle' % nethost,
    ),
    triangle_phi = device('nicos_mlz.refsans.devices.triangle.TriangleAngle',
        description = 'triangle_X',
        lowlevel = all_lowlevel,
        index = 1,
        tacodevice = '//%s/test/network/triangle' % nethost,
    ),
)
