description = 'Monochromator'

x_conf = configdata('localconfig.X_CONF')
y_conf = configdata('localconfig.Y_CONF')

chi1_conf = configdata('localconfig.CHI1_CONF')
chi2_conf = configdata('localconfig.CHI2_CONF')
chi3_conf = configdata('localconfig.CHI3_CONF')
chi4_conf = configdata('localconfig.CHI4_CONF')

omega_conf = configdata('localconfig.OMEGA_CONF')

tango_base = configdata('localconfig.tango_base') + 'device/mono/'

devices = dict(
    x_mon = device('nicos.devices.entangle.Motor',
                   description = x_conf['description'],
                   tangodevice = tango_base + 'x_mon',
                   precision = x_conf['precision'],
                   lowlevel = x_conf['lowlevel'],
                   abslimits = x_conf['abslimits'],
                   speed = x_conf['speed'],
                   unit = x_conf['unit'],
                   ),

   y_mon = device('nicos.devices.entangle.Motor',
                  description = y_conf['description'],
                  tangodevice = tango_base + 'y_mon',
                  precision = y_conf['precision'],
                  lowlevel = y_conf['lowlevel'],
                  abslimits = y_conf['abslimits'],
                  speed = y_conf['speed'],
                  unit = y_conf['unit'],
                  ),

   chi1 = device('nicos.devices.entangle.Motor',
                 description = chi1_conf['description'],
                 tangodevice = tango_base + 'chi1',
                 precision = chi1_conf['precision'],
                 lowlevel = chi1_conf['lowlevel'],
                 abslimits = chi1_conf['abslimits'],
                 speed = chi1_conf['speed'],
                 unit = chi1_conf['unit'],
                 ),

   chi2 = device('nicos.devices.entangle.Motor',
                 description = chi2_conf['description'],
                 tangodevice = tango_base + 'chi2',
                 precision = chi2_conf['precision'],
                 lowlevel = chi2_conf['lowlevel'],
                 abslimits = chi2_conf['abslimits'],
                 speed = chi2_conf['speed'],
                 unit = chi2_conf['unit'],
                 ),

   chi3 = device('nicos.devices.entangle.Motor',
                 description = chi3_conf['description'],
                 tangodevice = tango_base + 'chi3',
                 precision = chi3_conf['precision'],
                 lowlevel = chi3_conf['lowlevel'],
                 abslimits = chi3_conf['abslimits'],
                 speed = chi3_conf['speed'],
                 unit = chi3_conf['unit'],
                 ),

   chi4 = device('nicos.devices.entangle.Motor',
                 description = chi4_conf['description'],
                 tangodevice = tango_base + 'chi4',
                 precision = chi4_conf['precision'],
                 lowlevel = chi4_conf['lowlevel'],
                 abslimits = chi4_conf['abslimits'],
                 speed = chi4_conf['speed'],
                 unit = chi4_conf['unit'],
                 ),

    omega = device('nicos.devices.entangle.Motor',
                   description = omega_conf['description'],
                   tangodevice = tango_base + 'omega',
                   precision = omega_conf['precision'],
                   lowlevel = omega_conf['lowlevel'],
                   abslimits = omega_conf['abslimits'],
                   speed = omega_conf['speed'],
                   unit = omega_conf['unit'],
                   ),

    shutter = device('nicos.devices.entangle.DigitalOutput',
                     description = 'Shutter device switch',
                     tangodevice = tango_base + 'shutter',
                     fmtstr = '%#x',
                     lowlevel = False,
                     ),
)
