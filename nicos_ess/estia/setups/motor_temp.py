description = 'Temperature sensors for motors'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict()

desc = [f'sensor {s}' for s in range(6, 14)]
for sensor in range(6, 14):
    devices[f't_{sensor}'] = device('nicos.devices.epics.EpicsReadable',
        epicstimeout = 3.0,
        description = desc[sensor - 6],
        readpv = f'{pvprefix}m{sensor}-Temp',
        unit = 'C',
    )
