description = 'small goniometer to adjust sample on gonio'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']

devices = dict(
    gonio_top_theta = device('nicos.devices.tango.Motor',
        description = 'Top Theta axis motor',
        tangodevice = tango_base + 'sample/phy_mo2/top_theta_m',
    ),
    gonio_top_z = device('nicos.devices.generic.Axis',
        description = 'Top Z axis with offset',
        motor = 'gonio_top_z_motor',
        precision = 0.01,
        offset = 0.0,
    ),
    gonio_top_z_motor = device('nicos.devices.tango.Motor',
        description = 'Top Z axis motor dont care about the scala!',
        tangodevice = tango_base + 'sample/phy_mo2/top_z_m',
        lowlevel = True,
    ),
    gonio_top_phi = device('nicos.devices.tango.Motor',
        description = 'Top Phi axis motor',
        tangodevice = tango_base + 'sample/phy_mo2/top_phi_m',
    ),
)
