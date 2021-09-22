description = 'Sample environment'

alpha_conf = configdata('localconfig.ALPHA_CONF')
current_conf = configdata('localconfig.CURRENT_CONF')
b_conf = configdata('localconfig.B_CONF')

tango_base = configdata('localconfig.tango_base') + 'device/se/'


devices = dict(
    B = device('nicos.devices.generic.CalibratedMagnet',
               description = b_conf['description'],
               currentsource = 'current_source',
               calibration = b_conf['calibration'],
               ),
    current_source = device('nicos.devices.entangle.AnalogOutput',
                            description = current_conf['description'],
                            tangodevice = tango_base + "cs",
                            abslimits = current_conf['abslimits'],
                            lowlevel = current_conf['lowlevel'],
                            unit = current_conf['unit'],
                            ),

    alpha = device('nicos.devices.entangle.Motor',
                   description = alpha_conf['description'],
                   tangodevice = tango_base + 'alpha',
                   precision = alpha_conf['precision'],
                   lowlevel = alpha_conf['lowlevel'],
                   abslimits = alpha_conf['abslimits'],
                   speed = alpha_conf['speed'],
                   unit = alpha_conf['unit'],
                   ),
)
