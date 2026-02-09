description = 'Devices for Slit1'

pvprefixpmac1 = 'SQ:SANS-LLB:turboPmac1:'
pvprefixpmac2 = 'SQ:SANS-LLB:turboPmac2:'
pvprefixpmac4 = 'SQ:SANS-LLB:turboPmac4:'
pvprefixmmacs1 = 'SQ:SANS-LLB:masterMacs1:'

group = 'lowlevel'

devices = dict(
    sl1xn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit1 right',
        motorpv = pvprefixpmac2 + 'sl1xn',
        visibility = {'metadata','namespace'},
    ),
    sl1xp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit1 left',
        motorpv = pvprefixpmac2 + 'sl1xp',
        visibility = {'metadata','namespace'},
    ),
    sl1yn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit1 bottom',
        motorpv = pvprefixpmac2 + 'sl1yn',
        visibility = {'metadata','namespace'},
    ),
    sl1yp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit1 top',
        motorpv = pvprefixpmac2 + 'sl1yp',
        visibility = {'metadata','namespace'},
    ),
    # Are left right top and bottom correct here? they seem to be opposite?
    slit1 = device('nicos_sinq.sans_llb.devices.slit.EnableableSlit',
        description = 'Slit 1 behind col0',
        opmode = 'centered',
        coordinates = 'opposite',
        left = 'sl1xp',
        right = 'sl1xn',
        top = 'sl1yp',
        bottom = 'sl1yn',
        autodevice_visibility = {'metadata','namespace'},
        # TODO should we allow reference runs of all motors at once?
        # are these relative or absolute motors?
        # parallel_ref = True,
    ),
    sl1xw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis'
    ),
    sl1yw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis'
    ),
)

# it does not work to directly set this alias as the device comes from the attribute
startupcode = """
sl1xw.alias='slit1.width'
sl1yw.alias='slit1.height'
"""
