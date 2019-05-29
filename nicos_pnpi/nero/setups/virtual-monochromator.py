description = 'Virtual monochromator'

excludes = ['monochromator']

x_conf = configdata('localconfig.X_CONF')
y_conf = configdata('localconfig.Y_CONF')

chi1_conf = configdata('localconfig.CHI1_CONF')
chi2_conf = configdata('localconfig.CHI2_CONF')
chi3_conf = configdata('localconfig.CHI3_CONF')
chi4_conf = configdata('localconfig.CHI4_CONF')

omega_conf = configdata('localconfig.OMEGA_CONF')

devices = dict(
    x_mon = device('nicos.devices.generic.VirtualMotor',
                   description = x_conf['description'],
                   precision = x_conf['precision'],
                   visibility = x_conf['visibility'],
                   abslimits = x_conf['abslimits'],
                   speed = x_conf['speed'],
                   unit = x_conf['unit'],
                   ),

   y_mon = device('nicos.devices.generic.VirtualMotor',
                  description = y_conf['description'],
                  precision = y_conf['precision'],
                  visibility = y_conf['visibility'],
                  abslimits = y_conf['abslimits'],
                  speed = y_conf['speed'],
                  unit = y_conf['unit'],
                  ),

   chi1 = device('nicos.devices.generic.VirtualMotor',
                 description = chi1_conf['description'],
                 precision = chi1_conf['precision'],
                 visibility = chi1_conf['visibility'],
                 abslimits = chi1_conf['abslimits'],
                 speed = chi1_conf['speed'],
                 unit = chi1_conf['unit'],
                 ),

   chi2 = device('nicos.devices.generic.VirtualMotor',
                 description = chi2_conf['description'],
                 precision = chi2_conf['precision'],
                 visibility = chi2_conf['visibility'],
                 abslimits = chi2_conf['abslimits'],
                 speed = chi2_conf['speed'],
                 unit = chi2_conf['unit'],
                 ),

   chi3 = device('nicos.devices.generic.VirtualMotor',
                 description = chi3_conf['description'],
                 precision = chi3_conf['precision'],
                 visibility = chi3_conf['visibility'],
                 abslimits = chi3_conf['abslimits'],
                 speed = chi3_conf['speed'],
                 unit = chi3_conf['unit'],
                 ),

   chi4 = device('nicos.devices.generic.VirtualMotor',
                 description = chi4_conf['description'],
                 precision = chi4_conf['precision'],
                 visibility = chi4_conf['visibility'],
                 abslimits = chi4_conf['abslimits'],
                 speed = chi4_conf['speed'],
                 unit = chi4_conf['unit'],
                 ),

    omega = device('nicos.devices.generic.VirtualMotor',
                   description = omega_conf['description'],
                   precision = omega_conf['precision'],
                   visibility = omega_conf['visibility'],
                   abslimits = omega_conf['abslimits'],
                   speed = omega_conf['speed'],
                   unit = omega_conf['unit'],
                   ),

    shutter = device('nicos.devices.generic.ManualSwitch',
                     description = 'virtual shutter',
                     states = ['unknown', 'open', 'close'],
                     requires = {'level': 0},
                     ),

)

