description = 'Colimator'

x_gap_conf = configdata('localconfig.X_GAP_CONF')
y_gap_conf = configdata('localconfig.Y_GAP_CONF')

tango_base = configdata('localconfig.tango_base') + 'device/colimator/'

devices = dict(
    x_gap = device('nicos.devices.entangle.Motor',
                   description = x_gap_conf['description'],
                   tangodevice = tango_base + 'x_gap',
                   precision = x_gap_conf['precision'],
                   lowlevel = x_gap_conf['lowlevel'],
                   abslimits = x_gap_conf['abslimits'],
                   speed = x_gap_conf['speed'],
                   unit = x_gap_conf['unit'],
                   ),

   y_gap = device('nicos.devices.entangle.Motor',
                  description = y_gap_conf['description'],
                  tangodevice = tango_base + 'y_gap',
                  precision = y_gap_conf['precision'],
                  lowlevel = y_gap_conf['lowlevel'],
                  abslimits = y_gap_conf['abslimits'],
                  speed = y_gap_conf['speed'],
                  unit = y_gap_conf['unit'],
                  ),

    col = device('nicos.devices.generic.TwoAxisSlit',
                description = 'colimator gap',
                horizontal = 'x_gap',
                vertical = 'y_gap',
                )

)

