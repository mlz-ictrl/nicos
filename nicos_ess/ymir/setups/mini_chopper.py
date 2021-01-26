description = "The mini-chopper for YMIR"

pv_root = "Utg-Ymir:Chop-Drv-0101:"

devices = dict(
    Chopper_speed=device(
        "nicos.devices.epics.EpicsAnalogMoveable",
        description="The speed setpoint.",
        readpv="{}Spd_Stat".format(pv_root),
        writepv="{}Spd_SP".format(pv_root),
        abslimits=(0.0, 14),
    ),
    Chopper_status=device(
        "nicos.devices.epics.EpicsStringReadable",
        description="The chopper status.",
        readpv="{}Chop_Stat".format(pv_root),
    ),
)
