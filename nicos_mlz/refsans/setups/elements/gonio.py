description = 'Sample table devices'

group = 'lowlevel'


instrument_values = configdata('instrument.values')

tango_base1 = instrument_values['tango_base'] + 'sample/phy_mo1/'
tango_base2 = instrument_values['tango_base'] + 'sample/phy_mo2/'

devices = dict(
    gonio_theta = device('nicos.devices.generic.Axis',
        description = 'Theta axis',
        motor = 'gonio_theta_motor',
        coder = 'gonio_theta_enc',
        precision = 0.01,
    ),
    gonio_theta_motor = device('nicos.devices.tango.Motor',
        description = 'Theta axis motor',
        tangodevice = tango_base1 + 'theta_m',
        lowlevel = True,
    ),
    gonio_theta_enc = device('nicos.devices.tango.Sensor',
        description = 'Theta axis coder',
        tangodevice = tango_base1 + 'theta_e',
        lowlevel = True,
    ),
    gonio_phi = device('nicos.devices.generic.Axis',
        description = 'Phi axis',
        motor = 'gonio_phi_motor',
        coder = 'gonio_phi_enc',
        precision = 0.01,
    ),
    gonio_phi_motor = device('nicos.devices.tango.Motor',
        description = 'Phi axis motor',
        tangodevice = tango_base1 + 'phi_m',
        lowlevel = True,
    ),
    gonio_phi_enc = device('nicos.devices.tango.Sensor',
        description = 'Phi axis coder',
        tangodevice = tango_base1 + 'phi_e',
        lowlevel = True,
    ),
    gonio_omega = device('nicos.devices.generic.Axis',
        description = 'Omega axis',
        motor = 'gonio_omega_motor',
        coder = 'gonio_omega_enc',
        abslimits = [-2.1, 2.1],
        precision = 0.01,
    ),
    gonio_omega_motor = device('nicos.devices.tango.Motor',
        description = 'Omega axis motor',
        tangodevice = tango_base1 + 'omega_m',
        abslimits = [-2.1, 2.1],
        lowlevel = True,
    ),
    gonio_omega_enc = device('nicos.devices.tango.Sensor',
        description = 'Omega axis coder',
        tangodevice = tango_base1 + 'omega_e',
        lowlevel = True,
    ),
    gonio_y = device('nicos.devices.generic.Axis',
        description = 'Y axis. towards TOFTOF is plus',
        motor = 'gonio_y_motor',
        # coder = 'gonio_y_enc',
        precision = 0.01,
    ),
    gonio_y_motor = device('nicos.devices.tango.Motor',
        description = 'y axis motor',
        tangodevice = tango_base2 + 'y_m',
        lowlevel = True,
    ),
    gonio_y_enc = device('nicos.devices.tango.Sensor',
        description = 'y axis coder',
        tangodevice = tango_base2 + 'y_e',
        lowlevel = True,
    ),
    gonio_z = device('nicos.devices.generic.Axis',
        description = 'Z axis',
        motor = 'gonio_z_motor',
        # coder = 'gonio_z_enc',
        precision = 0.01,
    ),
    gonio_z_motor = device('nicos.devices.tango.Motor',
        description = 'Z axis motor',
        tangodevice = tango_base1 + 'z_m',
        lowlevel = True,
    ),
    gonio_z_enc = device('nicos.devices.tango.Sensor',
        description = 'Z axis coder',
        tangodevice = tango_base1 + 'z_e',
        lowlevel = True,
    ),
)
