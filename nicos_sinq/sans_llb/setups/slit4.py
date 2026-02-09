description = 'Devices for Slit4'

pvprefixpmac1 = 'SQ:SANS-LLB:turboPmac1:'
pvprefixpmac2 = 'SQ:SANS-LLB:turboPmac2:'
pvprefixpmac4 = 'SQ:SANS-LLB:turboPmac4:'
pvprefixmmacs1 = 'SQ:SANS-LLB:masterMacs1:'

group = 'lowlevel'

devices = dict(
    sl4xn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit4 right',
        motorpv = pvprefixmmacs1 + 'sl4xn',
        visibility = {'metadata','namespace'},
    ),
    sl4xp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit4 left',
        motorpv = pvprefixmmacs1 + 'sl4xp',
        visibility = {'metadata','namespace'},
    ),
    sl4yn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit4 bottom',
        motorpv = pvprefixmmacs1 + 'sl4yn',
        visibility = {'metadata','namespace'},
    ),
    sl4yp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit4 top',
        motorpv = pvprefixmmacs1 + 'sl4yp',
        visibility = {'metadata','namespace'},
    ),
    # Are left right top and bottom correct here? they seem to be opposite?
    slit4 = device('nicos_sinq.sans_llb.devices.slit.EnableableSlit',
        description = 'Slit 4 with behind col3',
        opmode = 'centered',
        coordinates = 'opposite',
        left = 'sl4xp',
        right = 'sl4xn',
        top = 'sl4yp',
        bottom = 'sl4yn',
        autodevice_visibility = {'metadata','namespace'},
        # TODO should we allow reference runs of all motors at once?
        # are these relative or absolute motors?
        # parallel_ref = True,
    ),
    sl4xw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis'
    ),
    sl4yw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis'
    ),
)

# it does not work to directly set this alias as the device comes from the attribute
startupcode = """
sl4xw.alias='slit4.width'
sl4yw.alias='slit4.height'
"""
