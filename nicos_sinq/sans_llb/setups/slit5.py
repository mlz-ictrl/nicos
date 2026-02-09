description = 'Devices for Slit5'

pvprefixpmac1 = 'SQ:SANS-LLB:turboPmac1:'
pvprefixpmac2 = 'SQ:SANS-LLB:turboPmac2:'
pvprefixpmac4 = 'SQ:SANS-LLB:turboPmac4:'
pvprefixmmacs1 = 'SQ:SANS-LLB:masterMacs1:'

group = 'lowlevel'

devices = dict(
    sl5xn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit5 right',
        motorpv = pvprefixmmacs1 + 'sl5xn',
        visibility = {'metadata','namespace'},
    ),
    sl5xp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit5 left',
        motorpv = pvprefixmmacs1 + 'sl5xp',
        visibility = {'metadata','namespace'},
    ),
    sl5yn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit5 bottom',
        motorpv = pvprefixmmacs1 + 'sl5yn',
        visibility = {'metadata','namespace'},
    ),
    sl5yp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit5 top',
        motorpv = pvprefixmmacs1 + 'sl5yp',
        visibility = {'metadata','namespace'},
    ),
    # Are left right top and bottom correct here? they seem to be opposite?
    slit5 = device('nicos_sinq.sans_llb.devices.slit.EnableableSlit',
        description = 'Slit 5 behind col4',
        opmode = 'centered',
        coordinates = 'opposite',
        left = 'sl5xp',
        right = 'sl5xn',
        top = 'sl5yp',
        bottom = 'sl5yn',
        autodevice_visibility = {'metadata','namespace'},
        # TODO should we allow reference runs of all motors at once?
        # are these relative or absolute motors?
        # parallel_ref = True,
    ),
    sl5xw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis'
    ),
    sl5yw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis'
    ),
)

# it does not work to directly set this alias as the device comes from the attribute
startupcode = """
sl5xw.alias='slit5.width'
sl5yw.alias='slit5.height'
"""
