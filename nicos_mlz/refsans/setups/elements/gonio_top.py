description = 'small goniometer to adjust sample on gonio'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    gonio_top_theta = device('nicos.devices.taco.Motor',
        description = 'Top Theta axis motor',
        tacodevice = '%s/phytron/kanal_10' % tacodev,
        abslimits = (-9.5, 10.5),
    ),
    gonio_top_z = device('nicos.devices.generic.Axis',
        description = 'Top Z axis motor with offset',
        motor = 'gonio_top_z_m',
        coder = 'gonio_top_z_m',
        precision = 0.01,
        offset = 0.0
    ),
    gonio_top_z_m = device('nicos.devices.taco.Motor',
        description = 'Top Z axis motor',
        tacodevice = '%s/phytron/kanal_11' % tacodev,
        abslimits = (-0.05, 15),
        lowlevel = True,
    ),
    gonio_top_phi = device('nicos.devices.taco.Motor',
        description = 'Top Phi axis motor, defect MP 04.06.2018 09:48:28',
        tacodevice = '%s/phytron/kanal_12' % tacodev,
        abslimits = (-10.5, 10.5),
        lowlevel = True,
    ),
)
