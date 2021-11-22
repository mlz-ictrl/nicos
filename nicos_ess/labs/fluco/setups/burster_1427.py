description = 'Burster precision resistance decade 1427 (resistance bridge)'

pv_root = 'E04-SEE-FLUCO:Rdec-Burster1427-01:'

devices = dict(
    burster_value=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The resistance?',
        readpv='{}value_RBV'.format(pv_root),
        writepv='{}value'.format(pv_root),
        epicstimeout=3.0,
        abslimits=(-1e308, 1e308),
    ),
    burster_function=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The current burster function',
        readpv='{}function_RBV'.format(pv_root),
        epicstimeout=3.0,
    ),
    burster_function_set=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Set the burster function',
        readpv='{}function'.format(pv_root),
        writepv='{}function'.format(pv_root),
    ),
    burster_idn=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The IDN of the device',
        readpv='{}idn'.format(pv_root),
        epicstimeout=3.0,
    ),
    burster_r0=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The resistance',
        readpv='{}r0_RBV'.format(pv_root),
        writepv='{}r0'.format(pv_root),
        epicstimeout=3.0,
        abslimits=(-1e308, 1e308),
    ),
    burster_status=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The status',
        readpv='{}status_RBV'.format(pv_root),
        epicstimeout=3.0,
    ),
    burster_terminal_r=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The resistance',
        readpv='{}terminal_RBV'.format(pv_root),
        writepv='{}terminal'.format(pv_root),
        epicstimeout=3.0,
        abslimits=(-1e308, 1e308),
    ),
)
