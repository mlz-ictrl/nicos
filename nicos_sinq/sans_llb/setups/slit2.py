description = 'Devices for Slit2'

pvprefixpmac1 = 'SQ:SANS-LLB:turboPmac1:'
pvprefixpmac2 = 'SQ:SANS-LLB:turboPmac2:'
pvprefixpmac4 = 'SQ:SANS-LLB:turboPmac4:'
pvprefixmmacs1 = 'SQ:SANS-LLB:masterMacs1:'

group = 'lowlevel'

devices = dict(
    sl2xn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit2 right',
        motorpv = pvprefixmmacs1 + 'sl2xn',
        visibility = {'metadata','namespace'},
    ),
    sl2xp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit2 left',
        motorpv = pvprefixmmacs1 + 'sl2xp',
        visibility = {'metadata','namespace'},
    ),
    sl2yn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit2 bottom',
        motorpv = pvprefixmmacs1 + 'sl2yn',
        visibility = {'metadata','namespace'},
    ),
    sl2yp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit2 top',
        motorpv = pvprefixmmacs1 + 'sl2yp',
        visibility = {'metadata','namespace'},
    ),
    # Are left right top and bottom correct here? they seem to be opposite?
    slit2 = device('nicos_sinq.sans_llb.devices.slit.EnableableSlit',
        description = 'Slit 2 behind col1',
        opmode = 'centered',
        coordinates = 'opposite',
        left = 'sl2xp',
        right = 'sl2xn',
        top = 'sl2yp',
        bottom = 'sl2yn',
        autodevice_visibility = {'metadata','namespace'},
        # TODO should we allow reference runs of all motors at once?
        # are these relative or absolute motors?
        # parallel_ref = True,
    ),
    sl2xw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis'
    ),
    sl2yw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis'
    ),
)

# it does not work to directly set this alias as the device comes from the attribute
startupcode = """
sl2xw.alias='slit2.width'
sl2yw.alias='slit2.height'
"""
