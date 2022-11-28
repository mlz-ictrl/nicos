description = 'NE9000 peristaltic pump'

pv_root = 'E04-SEE-FLUCO:NE9000-001:'

devices = dict(
    inside_diameter_9000=device(
        'nicos.devices.epics.EpicsStringReadable',
        description='The Inside diameter of the syringe',
        readpv='{}DIAMETER'.format(pv_root),
    ),
    pump_volume_9000=device(
        'nicos.devices.epics.EpicsAnalogMoveable',
        description='The volume to be pumped',
        readpv='{}VOLUME'.format(pv_root),
        writepv='{}SET_VOLUME'.format(pv_root),
        abslimits=(-1e308, 1e308),
    ),
    pump_volume_units_9000=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='The volume units',
        readpv='{}VOLUME_UNITS'.format(pv_root),
        writepv='{}SET_VOLUME_UNITS'.format(pv_root),
    ),
    pump_rate_9000=device(
        'nicos.devices.epics.EpicsAnalogMoveable',
        description='The pump rate',
        readpv='{}RATE'.format(pv_root),
        writepv='{}SET_RATE'.format(pv_root),
        abslimits=(-1e308, 1e308),
    ),
    pump_rate_units_9000=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='The rate units',
        readpv='{}RATE_UNITS'.format(pv_root),
        writepv='{}SET_RATE_UNITS'.format(pv_root),
    ),
    pump_direction_9000=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='The pump direction',
        readpv='{}DIRECTION'.format(pv_root),
        writepv='{}SET_DIRECTION'.format(pv_root),
    ),
    volume_withdrawn_9000=device(
        'nicos.devices.epics.EpicsReadable',
        description='The volume withdrawn',
        readpv='{}VOLUME_WITHDRAWN'.format(pv_root),
    ),
    volume_infused_9000=device(
        'nicos.devices.epics.EpicsReadable',
        description='The volume infused',
        readpv='{}VOLUME_INFUSED'.format(pv_root),
    ),
    pump_status_9000=device(
        'nicos.devices.epics.EpicsReadable',
        description='The pump status',
        readpv='{}STATUS'.format(pv_root),
        visibility=(),
    ),
    pump_message_9000=device(
        'nicos.devices.epics.EpicsStringReadable',
        description='The pump message',
        readpv='{}MESSAGE'.format(pv_root),
        visibility=(),
    ),
    start_pumping_9000=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Start pumping',
        readpv='{}RUN'.format(pv_root),
        writepv='{}RUN'.format(pv_root),
    ),
    pause_pumping_9000=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Pause pumping',
        readpv='{}PAUSE'.format(pv_root),
        writepv='{}PAUSE'.format(pv_root),
    ),
    stop_pumping_9000=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Stop pumping',
        readpv='{}STOP'.format(pv_root),
        writepv='{}STOP'.format(pv_root),
    ),
    seconds_to_pause_9000=device(
        'nicos.devices.epics.EpicsAnalogMoveable',
        description='How long to pause for',
        readpv='{}SET_PAUSE'.format(pv_root),
        writepv='{}SET_PAUSE'.format(pv_root),
        abslimits=(-1e308, 1e308),
    ),
    zero_volume_withdrawn_9000=device(
        'nicos.devices.epics.EpicsReadable',
        description='Zero volume withdrawn and infused',
        readpv='{}CLEAR_V_DISPENSED'.format(pv_root),
    ),
)
