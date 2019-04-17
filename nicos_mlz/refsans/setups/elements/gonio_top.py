description = 'small goniometer to adjust sample on gonio'

group = 'optional'

tango_base = 'tango://refsanshw:10000/sample/phy_mo2/'

devices = dict(
    gonio_top_theta = device('nicos.devices.tango.Motor',
        description = 'Top Theta axis motor',
        tangodevice = tango_base + 'top_theta_m',
        abslimits = (-9.5, 10.5),
    ),
    gonio_top_z = device('nicos.devices.generic.Axis',
        description = 'Top Z axis with offset',
        motor = 'gonio_top_z_m',
        coder = 'gonio_top_z_m',
        precision = 0.01,
        offset = 0.0,
    ),
    gonio_top_z_m = device('nicos.devices.tango.Motor',
        description = 'Top Z axis motor',
        tangodevice = tango_base + 'top_z_m',
        abslimits = (-0.05, 16),
        lowlevel = True,
    ),
    gonio_top_phi = device('nicos.devices.tango.Motor',
        description = 'Top Phi axis motor',
        tangodevice = tango_base + 'top_phi_m',
        abslimits = (-10.5, 10.5),
    ),
)
