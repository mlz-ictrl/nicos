description = 'Devices for Slit0'

pvprefixpmac1 = 'SQ:SANS-LLB:turboPmac1:'
pvprefixpmac2 = 'SQ:SANS-LLB:turboPmac2:'
pvprefixpmac4 = 'SQ:SANS-LLB:turboPmac4:'
pvprefixmmacs1 = 'SQ:SANS-LLB:masterMacs1:'

group = 'lowlevel'

devices = dict(
    sl0xp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit0 left',
        motorpv = pvprefixpmac1 + 'sl0xp',
        visibility = {'metadata','namespace'},
    ),
    sl0xn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit0 right',
        motorpv = pvprefixpmac2 + 'sl0xn',
        visibility = {'metadata','namespace'},
    ),
    sl0yp = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit0 top',
        motorpv = pvprefixpmac2 + 'sl0yp',
        visibility = {'metadata','namespace'},
    ),
    sl0yn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'slit0 bottom',
        motorpv = pvprefixpmac1 + 'sl0yn',
        visibility = {'metadata','namespace'},
    ),
    # Are left right top and bottom correct here? they seem to be opposite?
    slit0 = device('nicos_sinq.sans_llb.devices.slit.EnableableSlit',
        description = 'Slit 0 behind mask changer',
        opmode = 'centered',
        coordinates = 'opposite',
        left = 'sl0xp',
        right = 'sl0xn',
        top = 'sl0yp',
        bottom = 'sl0yn',
        autodevice_visibility = {'metadata','namespace'},
        # TODO should we allow reference runs of all motors at once?
        # are these relative or absolute motors?
        # parallel_ref = True,
    ),
    sl0xw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis',
    ),
    sl0yw = device('nicos.core.device.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis',
    ),
)

# it does not work to directly set this alias as the device comes from the attribute
startupcode = """
sl0xw.alias='slit0.width'
sl0yw.alias='slit0.height'
"""
