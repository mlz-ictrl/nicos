description = "The mini-chopper for YMIR"

pv_root = "Utg-Ymir:Chop-Drv-0101:"

devices = dict(
    Chopper_status=device(
        "nicos.devices.epics.EpicsStringReadable",
        description="The chopper status.",
        readpv="{}Chop_Stat".format(pv_root),
    ),
    Chopper_speed=device(
        "nicos.devices.epics.EpicsAnalogMoveable",
        description="The current speed.",
        readpv="{}Spd_Stat".format(pv_root),
        writepv="{}Spd_SP".format(pv_root),
        abslimits=(0.0, 14),
    ),
    Chopper_delay=device(
        "nicos.devices.epics.EpicsAnalogMoveable",
        description="The current delay.",
        readpv="{}Chopper-Delay-SP".format(pv_root),
        writepv="{}Chopper-Delay-SP".format(pv_root),
        abslimits=(0.0, 71428571.0),
    ),
)
