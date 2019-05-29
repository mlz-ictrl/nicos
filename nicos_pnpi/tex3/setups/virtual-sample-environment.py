description = 'Virtual Sample Environment movenments'

excludes = ['sample-environment']

tango_base = configdata('localconfig.tango_base')

omega_conf = configdata('localconfig.OMEGA_CONF')
phi_conf = configdata('localconfig.PHI_CONF')
chi_conf = configdata('localconfig.CHI_CONF')
theta_conf = configdata('localconfig.THETA_CONF')


devices = dict(
    omega = device('nicos.devices.generic.VirtualMotor',
                   description = omega_conf['description'],
                   precision = omega_conf['precision'],
                   visibility = omega_conf['visibility'],
                   abslimits = omega_conf['abslimits'],
                   speed = omega_conf['speed'],
                   unit = omega_conf['unit'],
                   ),
    phi = device('nicos.devices.generic.VirtualMotor',
                 description = phi_conf['description'],
                 precision = phi_conf['precision'],
                 visibility = phi_conf['visibility'],
                 abslimits = phi_conf['abslimits'],
                 speed = phi_conf['speed'],
                 unit = phi_conf['unit'],
                 ),
    chi = device('nicos.devices.generic.VirtualMotor',
                 description = chi_conf['description'],
                 precision = chi_conf['precision'],
                 visibility = chi_conf['visibility'],
                 abslimits = chi_conf['abslimits'],
                 speed = chi_conf['speed'],
                 unit = chi_conf['unit'],
                 ),
    theta = device('nicos.devices.generic.VirtualMotor',
                   description = theta_conf['description'],
                   precision = theta_conf['precision'],
                   visibility = theta_conf['visibility'],
                   abslimits = theta_conf['abslimits'],
                   speed = theta_conf['speed'],
                   unit = theta_conf['unit'],
                   ),
)
