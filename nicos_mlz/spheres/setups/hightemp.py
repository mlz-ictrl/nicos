description = "Hightemperature setup for SPHERES"

group = 'basic'

includes = ['spheres',
            'cct6']

startupcode = """
cct6_c_temperature.samplestick = 'ht'\n
cct6_c_temperature.userlimits = (100, 500)
"""