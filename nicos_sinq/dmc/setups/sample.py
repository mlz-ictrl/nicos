description = 'Sample devices for SINQ DMC.'

pvprefix = 'SQ:DMC:turboPmac2:'

devices = dict(
    a3s = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample omega motor',
        motorpv = f'{pvprefix}A3',
        errormsgpv = f'{pvprefix}A3-MsgTxt',
        can_disable = True,
    ),
    a3 = device('nicos.core.device.DeviceAlias',
        description = 'Alias for sample rotation',
        alias = 'a3s',
        devclass = 'nicos.core.device.Moveable'
    ),
)
