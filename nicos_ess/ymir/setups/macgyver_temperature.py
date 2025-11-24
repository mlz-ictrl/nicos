description = 'The temperature inputs of the MacGyver box.'

pv_root = 'se-macgyver-001:'

devices = dict()

for i in range(1, 5):
    devices[f'macgyver_temperature_in_{i}'] = device(
        'nicos.devices.epics.EpicsBoolReadable',
        description=f'MacGyver box temperature in {i}',
        readpv=f'{pv_root}thermo_{i}-R',
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    )
