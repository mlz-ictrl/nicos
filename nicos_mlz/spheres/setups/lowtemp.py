description = "Lowtemperature setup for SPHERES" \
              "Contains: SIS, doppler, shutter, sps and cct6"

group = 'basic'

includes = ['spheres',
            'cct6']

startupcode = """
cct6_c_temperature.samplestick = 'lt'\n
cct6_c_temperature.userlimits = (0, 350)
"""