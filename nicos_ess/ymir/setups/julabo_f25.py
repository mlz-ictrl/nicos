description = 'Julabo F25 for the Huginn-sans.'

pv_root = 'SES-HGNSANS-01:WTctrl-JUL25HL-001:'

devices = dict(
    T_julabo=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The temperature',
        readpv='{}TEMP'.format(pv_root),
        writepv='{}TEMP:SP1'.format(pv_root),
        targetpv='{}TEMP:SP1:RBV'.format(pv_root),
    ),
    julabo_status=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='The status',
        readpv='{}MODE'.format(pv_root),
        writepv='{}MODE:SP'.format(pv_root),
    ),
    T_julabo_external=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The external sensor temperature',
        readpv='{}EXTT'.format(pv_root),
        visibility=(),
    ),
    julabo_external_enabled=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='Whether the external sensor is enabled',
        readpv='{}EXTSENS'.format(pv_root),
        visibility=(),
    ),
    julabo_internal_P=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal P value',
        readpv='{}INTP'.format(pv_root),
        writepv='{}INTP:SP'.format(pv_root),
        visibility=(),
    ),
    julabo_internal_I=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal I value',
        readpv='{}INTI'.format(pv_root),
        writepv='{}INTI:SP'.format(pv_root),
        visibility=(),
    ),
    julabo_internal_D=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal D value',
        readpv='{}INTD'.format(pv_root),
        writepv='{}INTD:SP'.format(pv_root),
        visibility=(),
    ),
)
