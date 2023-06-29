description = 'The solid-state relays of the MacGyver box.'

pv_root = 'se-macgyver-001:'

devices = dict(
    macgyver_relay_1=device(
        'nicos.devices.epics.pva.EpicsBoolMoveable',
        description='MacGyver box relay 1',
        readpv='{}relay_1-R'.format(pv_root),
        writepv='{}relay_1-S'.format(pv_root),
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    ),
    macgyver_relay_2=device(
        'nicos.devices.epics.pva.EpicsBoolMoveable',
        description='MacGyver box relay 2',
        readpv='{}relay_2-R'.format(pv_root),
        writepv='{}relay_2-S'.format(pv_root),
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    ),
    macgyver_relay_3=device(
        'nicos.devices.epics.pva.EpicsBoolMoveable',
        description='MacGyver box relay 3',
        readpv='{}relay_3-R'.format(pv_root),
        writepv='{}relay_3-S'.format(pv_root),
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    ),
    macgyver_relay_4=device(
        'nicos.devices.epics.pva.EpicsBoolMoveable',
        description='MacGyver box relay 4',
        readpv='{}relay_4-R'.format(pv_root),
        writepv='{}relay_4-S'.format(pv_root),
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    ),
)
