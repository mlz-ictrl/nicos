description = 'Vinci pump'

pv_root = 'utg-vincipump-001:Dr1:'

devices = dict(
    vinci_volume=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The volume',
        readpv='{}Volume'.format(pv_root),
    ),
    vinci_flow=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The flow',
        readpv='{}Flow'.format(pv_root),
    ),
    vinci_pressure=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The pressure',
        readpv='{}Pressure'.format(pv_root),
        writepv='{}PM_Press_SP'.format(pv_root),
        abslimits=(0, 200),
    ),
    vinci_start=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Set the burster function',
        readpv='{}Start_Cmd'.format(pv_root),
        writepv='{}Start_Cmd'.format(pv_root),
        visibility=(),
    ),

)
