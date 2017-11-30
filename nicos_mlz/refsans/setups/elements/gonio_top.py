description = 'smal goniometer to adjust sample on gonio'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    gonio_top_theta = device('nicos.devices.taco.Motor',
        description = 'Top Theta axis motor',
        tacodevice = '%s/phytron/kanal_10' % tacodev,
        abslimits = (-9.5, 10.5),
    ),
    gonio_top_z = device('nicos.devices.taco.Motor',
        description = 'Top Z axis motor',
        tacodevice = '%s/phytron/kanal_11' % tacodev,
        abslimits = (-0.05, 15),
    ),
    gonio_top_phi = device('nicos.devices.taco.Motor',
        description = 'Top Phi axis motor',
        tacodevice = '%s/phytron/kanal_12' % tacodev,
        abslimits = (-10.5, 10.5),
    ),
)
