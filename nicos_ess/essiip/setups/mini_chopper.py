description = "The mini-chopper."

pv_root = "LabS-VIP:Chop-Drv-0101:"

devices = dict(
    Chopper_speed=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The speed setpoint.",
        readpv="{}Spd_Stat".format(pv_root),
        writepv="{}Spd_SP".format(pv_root),
        abslimits=(0.0, 140),
    ),
    Chopper_status=device(
        "nicos_ess.devices.epics.base.EpicsStringReadableEss",
        description="The chopper status.",
        readpv="{}Chop_Stat".format(pv_root),
    ),
)

