description = 'Devices for Slit3'

pvprefixpmac1 = 'SQ:SANS-LLB:turboPmac1:'
pvprefixpmac2 = 'SQ:SANS-LLB:turboPmac2:'
pvprefixpmac4 = 'SQ:SANS-LLB:turboPmac4:'
pvprefixmmacs1 = 'SQ:SANS-LLB:masterMacs1:'

group = 'lowlevel'

devices = dict(
    sl3xn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit3 right',
        motorpv = pvprefixmmacs1 + 'sl3xn',
        visibility = {'metadata','namespace'},
    ),
    sl3xp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit3 left',
        motorpv = pvprefixmmacs1 + 'sl3xp',
        visibility = {'metadata','namespace'},
    ),
    sl3yn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit3 bottom',
        motorpv = pvprefixmmacs1 + 'sl3yn',
        visibility = {'metadata','namespace'},
    ),
    sl3yp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit3 top',
        motorpv = pvprefixmmacs1 + 'sl3yp',
        visibility = {'metadata','namespace'},
    ),
    # Are left right top and bottom correct here? they seem to be opposite?
    slit3 = device('nicos_sinq.sans_llb.devices.slit.EnableableSlit',
        description = 'Slit 3 behind col2',
        opmode = 'centered',
        coordinates = 'opposite',
        left = 'sl3xp',
        right = 'sl3xn',
        top = 'sl3yp',
        bottom = 'sl3yn',
        autodevice_visibility = {'metadata','namespace'},
        # TODO should we allow reference runs of all motors at once?
        # are these relative or absolute motors?
        # parallel_ref = True,
    ),
    sl3xw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis'
    ),
    sl3yw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis'
    ),
)

# it does not work to directly set this alias as the device comes from the attribute
startupcode = """
sl3xw.alias='slit3.width'
sl3yw.alias='slit3.height'
"""
