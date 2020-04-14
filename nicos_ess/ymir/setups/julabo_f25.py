description = "Julabo F25 at Utgard Lab."

pv_root = "SES-HGNSANS-01:WTctrl-JUL25HL-001:"

devices = dict(
    T_julabo=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The temperature",
        readpv="{}TEMP".format(pv_root),
        writepv="{}TEMP:SP1".format(pv_root),
        targetpv="{}TEMP:SP1:RBV".format(pv_root),
        epicstimeout=3.0,
        precision=0.1,
        timeout=None,
        window=30.0,
    ),
    julabo_status=device(
        "nicos_ess.devices.epics.extensions.EpicsMappedMoveable",
        description="The status",
        readpv="{}MODE".format(pv_root),
        writepv="{}MODE:SP".format(pv_root),
        mapping={"OFF": 0, "ON": 1},
    ),
    T_julabo_external=device(
        "nicos_ess.devices.epics.base.EpicsReadableEss",
        description="The external sensor temperature",
        readpv="{}EXTT".format(pv_root),
        lowlevel=True,
        epicstimeout=3.0,
    ),
    julabo_external_enabled=device(
        "nicos_ess.devices.epics.base.EpicsStringReadableEss",
        description="Whether the external sensor is enabled",
        readpv="{}EXTSENS".format(pv_root),
        lowlevel=True,
        epicstimeout=3.0,
    ),
    julabo_internal_P=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The internal P value",
        readpv="{}INTP".format(pv_root),
        writepv="{}INTP:SP".format(pv_root),
        lowlevel=True,
        epicstimeout=3.0,
    ),
    julabo_internal_I=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The internal I value",
        readpv="{}INTI".format(pv_root),
        writepv="{}INTI:SP".format(pv_root),
        lowlevel=True,
        epicstimeout=3.0,
    ),
    julabo_internal_D=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The internal D value",
        readpv="{}INTD".format(pv_root),
        writepv="{}INTD:SP".format(pv_root),
        lowlevel=True,
        epicstimeout=3.0,
    ),
)

