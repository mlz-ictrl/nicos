description = 'Devices for the sample table'

pvpref = 'SQ:ZEBRA:turboPmac1:'

devices = dict(
    om_raw = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample rotation',
        motorpv = pvpref + 'SOM',
    ),
    om = device('nicos.core.device.DeviceAlias',
        description = 'Alias for om',
        alias = 'om_raw',
        devclass = 'nicos.core.device.Moveable'
    ),
    sx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample X translation',
        motorpv = pvpref + 'SX',
    ),
    sy = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample Y translation',
        motorpv = pvpref + 'SY',
    ),
    sz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample lift',
        motorpv = pvpref + 'SZ',
    ),
    stt = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Two Theta detector',
        motorpv = pvpref + 'STT',
    ),
)
"""
    Not available most of the time
    sgl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample lower goniometer',
        motorpv = pvpref + 'SGL',
    ),
    sgu = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample upper goniometer',
        motorpv = pvpref + 'SGU',
    ),
"""
alias_config = {'om': {'om_raw': 10}}
