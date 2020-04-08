description = "The Huginn SANS system."

pv_root = "SES-HGNSANS-01:"
pv_root_ls_1 = "{}Tctrl-LS336-001:".format(pv_root)
pv_root_ls_2 = "{}Tctrl-LS336-002:".format(pv_root)
pv_root_ls_3 = "{}Tctrl-LS336-003:".format(pv_root)

devices = dict(
    T_cuvette_1=device(
        "nicos_ess.devices.epics.base.EpicsReadableEss",
        description="The cuvette temperature",
        readpv="{}KRDG0".format(pv_root_ls_1),
    ),
    T_cuvette_1_setpoint=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The setpoint for the cuvette",
        readpv="{}SETP3".format(pv_root_ls_1),
        writepv="{}SETP_S3".format(pv_root_ls_1),
        abslimits=(0.0, 400),
    ),
    T_cuvette_2=device(
        "nicos_ess.devices.epics.base.EpicsReadableEss",
        description="The cuvette temperature",
        readpv="{}KRDG1".format(pv_root_ls_1),
    ),
    T_cuvette_2_setpoint=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The setpoint for the cuvette",
        readpv="{}SETP4".format(pv_root_ls_1),
        writepv="{}SETP_S4".format(pv_root_ls_1),
        abslimits=(0.0, 400),
    ),
    T_cuvette_3=device(
        "nicos_ess.devices.epics.base.EpicsReadableEss",
        description="The cuvette temperature",
        readpv="{}KRDG0".format(pv_root_ls_2),
    ),
    T_cuvette_3_setpoint=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The setpoint for the cuvette",
        readpv="{}SETP3".format(pv_root_ls_2),
        writepv="{}SETP_S3".format(pv_root_ls_2),
        abslimits=(0.0, 400),
    ),
    T_cuvette_4=device(
        "nicos_ess.devices.epics.base.EpicsReadableEss",
        description="The cuvette temperature",
        readpv="{}KRDG1".format(pv_root_ls_2),
    ),
    T_cuvette_4_setpoint=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The setpoint for the cuvette",
        readpv="{}SETP4".format(pv_root_ls_2),
        writepv="{}SETP_S4".format(pv_root_ls_2),
        abslimits=(0.0, 400),
    ),
    T_cuvette_5=device(
        "nicos_ess.devices.epics.base.EpicsReadableEss",
        description="The cuvette temperature",
        readpv="{}KRDG0".format(pv_root_ls_3),
    ),
    T_cuvette_5_setpoint=device(
        "nicos_ess.devices.epics.base.EpicsAnalogMoveableEss",
        description="The setpoint for the cuvette",
        readpv="{}SETP3".format(pv_root_ls_3),
        writepv="{}SETP_S3".format(pv_root_ls_3),
        abslimits=(0.0, 400),
    ),
)

