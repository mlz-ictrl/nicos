description = 'Julabo controlled via Octopy'

pv_root = 'se-fhcc01:se-secop:tctrl-'

devices = dict(
    julabo_octo_T=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The temperature',
        readpv='{}Temperature-R'.format(pv_root),
        writepv='{}TemperatureSP1-S'.format(pv_root),
        targetpv='{}TemperatureSP1-R'.format(pv_root),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_mode=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='The status',
        readpv='{}Mode-R'.format(pv_root),
        writepv='{}Mode-S'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    julabo_octo_external_T=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The external sensor temperature',
        readpv='{}TempExtSensor-R'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    julabo_octo_external_enabled=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Use external or internal sensor',
        readpv='{}ExternalSensor-R'.format(pv_root),
        writepv='{}ExternalSensor-S'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    julabo_octo_internal_P=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal P value',
        readpv='{}IntP-R'.format(pv_root),
        writepv='{}IntP-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_internal_I=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal I value',
        readpv='{}IntI-R'.format(pv_root),
        writepv='{}IntI-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_internal_D=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal D value',
        readpv='{}IntD-S'.format(pv_root),
        writepv='{}IntD-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_safety=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The safety sensor temperature',
        readpv='{}TempSafetySensor-R'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    julabo_octo_max_cooling=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The maximum cooling power %',
        readpv='{}MaxCoolPower-R'.format(pv_root),
        writepv='{}MaxCoolPower-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_max_heating=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The maximum heating power %',
        readpv='{}MaxHeatPower-R'.format(pv_root),
        writepv='{}MaxHeatPower-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_heating_power=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The heating power being used %',
        readpv='{}Power-R'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    julabo_octo_internal_slope=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The internal slope',
        readpv='{}InternalSlope-R'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    julabo_octo_external_P=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal P value',
        readpv='{}ExtP-R'.format(pv_root),
        writepv='{}ExtP-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_external_I=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal I value',
        readpv='{}ExtI-R'.format(pv_root),
        writepv='{}ExtI-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_external_D=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The internal D value',
        readpv='{}ExtD-R'.format(pv_root),
        writepv='{}ExtD-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_high_limit=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The high temp warning limit',
        readpv='{}TempHighLimit-R'.format(pv_root),
        writepv='{}TempHighLimit-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_low_limit=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The low temp warning limit',
        readpv='{}TempLowLimit-R'.format(pv_root),
        writepv='{}TempLowLimit-S'.format(pv_root),
        visibility=(),
        abslimits=(-1e308, 1e308),
        pva=True,
        monitor=True,
    ),
    julabo_octo_status=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The status',
        readpv='{}StatusNumber-R'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    julabo_octo_version=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The software version',
        readpv='{}Version-R'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    julabo_octo_online=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='Whether it is responsive',
        readpv='{}Online-R'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    julabo_octo_barcode=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The unique model number',
        readpv='{}Barcode-R'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
)
