description = 'Basic setup for SPHERES containing sis detector, doppler, ' \
              'sps selector and shutter'

group = 'basic'

includes = [
    'sis',
    'doppler',
    'sps',
    'shutter',
    'memograph',
    'selector',
    'alias_T',
    'cct6',
]

startupcode = 'SetDetectors(sis)\n' \
              'SetEnvironment(cct6_c_temperature, cct6_setpoint)'
