description = 'The analog inputs of the MacGyver box.'

pv_root = 'se-macgyver-001:'

devices = dict()

for i in range(1, 5):
    devices[f'macgyver_analog_in_{i}'] = device(
        'nicos.devices.epics.pva.EpicsBoolReadable',
        description=f'MacGyver box analog in {i}',
        readpv=f'{pv_root}analog_in_{i}-R',
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    )
