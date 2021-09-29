description = 'Virtual sample environment'

excludes = ['se']

alpha_conf = configdata('localconfig.ALPHA_CONF')
current_conf = configdata('localconfig.CURRENT_CONF')
b_conf = configdata('localconfig.B_CONF')

devices = dict(
    B = device('nicos.devices.generic.CalibratedMagnet',
               description = b_conf['description'],
               currentsource = 'current_source',
               calibration = b_conf['calibration'],
               ),
    current_source = device('nicos.devices.generic.VirtualMotor',
                            description = current_conf['description'],
                            abslimits = current_conf['abslimits'],
                            lowlevel = current_conf['lowlevel'],
                            speed = 0.9,
                            unit = current_conf['unit'],
                            ),

    alpha = device('nicos.devices.generic.VirtualMotor',
                   description = alpha_conf['description'],
                   precision = alpha_conf['precision'],
                   lowlevel = alpha_conf['lowlevel'],
                   abslimits = alpha_conf['abslimits'],
                   speed = alpha_conf['speed'],
                   unit = alpha_conf['unit'],
                   ),

    fb = device('nicos.devices.generic.ManualSwitch',
                description = 'Flipper before sample table',
                states = ['unknown', 'off', 'on'],
                requires = {'level': 0},
                ),

    fa = device('nicos.devices.generic.ManualSwitch',
                description = 'Flipper after sample table',
                states = ['unknown', 'off', 'on'],
                requires = {'level': 0},
                ),

)
