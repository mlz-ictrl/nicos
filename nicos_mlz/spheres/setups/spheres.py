description = 'Basic setup for SPHERES containing sis detector, doppler, ' \
              'sps selector and shutter'

group = 'basic'

includes = ['sis',
            'doppler',
            'cct6',
            'sps',
            'shutter',
            'memograph',
            'selector',
            ]

startupcode = 'SetDetectors(sis)\n' \
              'SetEnvironment(cct6_c_temperature, cct6_setpoint)'
