description = 'The analog outputs of the MacGyver box.'

pv_root = 'se-macgyver-001:'

devices = dict()

for i in range(1, 5):
    devices[f'macgyver_analog_out_{i}'] = device(
        'nicos.devices.epics.EpicsAnalogMoveable',
        description=f'MacGyver box analog out {i}',
        readpv=f'{pv_root}analog_out_{i}-R',
        writepv=f'{pv_root}analog_out_{i}-S',
        precision=0.0001,
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    )
