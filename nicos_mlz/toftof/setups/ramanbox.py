description = 'Setup for Raman sprectroscopy'

group = 'plugplay'

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'{setupname}_motor1': device('nicos.devices.entangle.MotorAxis',
        description = 'Newport rotation axis 1',
        tangodevice = tango_base + 'newport/motor1',
        fmtstr = '%.3f',
        unit = 'deg',
    ),
    f'{setupname}_motor2': device('nicos.devices.entangle.MotorAxis',
        description = 'Newport rotation axis 2',
        tangodevice = tango_base + 'newport/motor2',
        fmtstr = '%.3f',
        unit = 'deg',
    ),
}

monitor_blocks = dict(
    default = Block(f'TOFTOF-RAMANBOX', [
        BlockRow(
            Field(name='motor1', dev=f'{setupname}_motor1', width=12),
            Field(name='motor2', dev=f'{setupname}_motor2', width=12),
        ),
    ], setups=setupname),
)
