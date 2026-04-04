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
                   visibility = x_conf['visibility'],
                   unit = x_conf['unit'],
                   ),

   y_mon = device('nicos.devices.entangle.Motor',
                  description = y_conf['description'],
                  tangodevice = tango_base + 'y_mon',
                  precision = y_conf['precision'],
                  visibility = y_conf['visibility'],
                  unit = y_conf['unit'],
                  ),

   chi1 = device('nicos.devices.entangle.Motor',
                 description = chi1_conf['description'],
                 tangodevice = tango_base + 'chi1',
                 precision = chi1_conf['precision'],
                 visibility = chi1_conf['visibility'],
                 unit = chi1_conf['unit'],
                 ),

   chi2 = device('nicos.devices.entangle.Motor',
                 description = chi2_conf['description'],
                 tangodevice = tango_base + 'chi2',
                 precision = chi2_conf['precision'],
                 visibility = chi2_conf['visibility'],
                 unit = chi2_conf['unit'],
                 ),

   chi3 = device('nicos.devices.entangle.Motor',
                 description = chi3_conf['description'],
                 tangodevice = tango_base + 'chi3',
                 precision = chi3_conf['precision'],
                 visibility = chi3_conf['visibility'],
                 unit = chi3_conf['unit'],
                 ),

   chi4 = device('nicos.devices.entangle.Motor',
                 description = chi4_conf['description'],
                 tangodevice = tango_base + 'chi4',
                 precision = chi4_conf['precision'],
                 visibility = chi4_conf['visibility'],
                 unit = chi4_conf['unit'],
                 ),

    omega = device('nicos.devices.entangle.Motor',
                   description = omega_conf['description'],
                   tangodevice = tango_base + 'omega',
                   precision = omega_conf['precision'],
                   visibility = omega_conf['visibility'],
                   unit = omega_conf['unit'],
                   ),

    shutter = device('nicos.devices.entangle.DigitalOutput',
                     description = 'Shutter device switch',
                     tangodevice = tango_base + 'shutter',
                     fmtstr = '%#x',
                     ),
)
