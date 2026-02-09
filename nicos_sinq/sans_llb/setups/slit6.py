description = 'Devices for Slit6'

pvprefixpmac1 = 'SQ:SANS-LLB:turboPmac1:'
pvprefixpmac2 = 'SQ:SANS-LLB:turboPmac2:'
pvprefixpmac4 = 'SQ:SANS-LLB:turboPmac4:'
pvprefixmmacs1 = 'SQ:SANS-LLB:masterMacs1:'

group = 'lowlevel'

devices = dict(
    sl6xn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit6 right',
        motorpv = pvprefixmmacs1 + 'sl6xn',
        visibility = {'metadata','namespace'},
    ),
    sl6xp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit6 left',
        motorpv = pvprefixmmacs1 + 'sl6xp',
        visibility = {'metadata','namespace'},
    ),
    sl6yn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit6 bottom',
        motorpv = pvprefixmmacs1 + 'sl6yn',
        visibility = {'metadata','namespace'},
    ),
    sl6yp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit6 top',
        motorpv = pvprefixmmacs1 + 'sl6yp',
        visibility = {'metadata','namespace'},
    ),
    # Are left right top and bottom correct here? they seem to be opposite?
    slit6 = device('nicos_sinq.sans_llb.devices.slit.EnableableSlit',
        description = 'Slit 6 behind col5',
        opmode = 'centered',
        coordinates = 'opposite',
        left = 'sl6xp',
        right = 'sl6xn',
        top = 'sl6yp',
        bottom = 'sl6yn',
        autodevice_visibility = {'metadata','namespace'},
        # TODO should we allow reference runs of all motors at once?
        # are these relative or absolute motors?
        # parallel_ref = True,
    ),
    sl6xw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis'
    ),
    sl6yw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis'
    ),
    sl6_distance = device('nicos.devices.generic.ManualMove',
                          description='Distance from Sample to Slit6',
                          abslimits=(1000, 3000),
                          unit='mm'),
)

# it does not work to directly set this alias as the device comes from the attribute
startupcode = """
sl6xw.alias='slit6.width'
sl6yw.alias='slit6.height'
"""
