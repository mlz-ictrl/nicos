description = 'Battery temperature sensors'

# Devices run on a raspberry as entangle devices

tangobase = f'tango://{setupname}:10000/box/sensor/'

group = 'plugplay'

devices = dict(
)

for i in range(1, 9):
    devices[f'T_{setupname}_{i}'] = device('nicos.devices.entangle.Sensor',
        description = f'{setupname.capitalize()} temperature {i}',
        tangodevice = f'{tangobase}{i}',
        pollinterval = 30,
        maxage = 35,
    )
