# -*- coding: utf-8 -*-

description = "Hexapod control"
group = "optional"

excludes = []

tango_base = "tango://phys.maria.frm2:10000/maria/"

hexapod_workspaces = [
    # (workspace_id, workspace_definition_list)
    #
    # workspace_definition_list:
    # [xn, xp, yn, yp, zn, zp, rzn, rzp, ryn, ryp,
    #  rxn, rxp, tx, ty, tz, rz, ry, rx]
    (
        10, [
            -50., 50., -50., 50., -50., 50., -190., 120., -5., 5., -5., 5., 0.,
            0., 0., 0., 0., 0.
        ]
    ),
    # (
    #     11, [ ]
    # ),
]

devices = dict(
    hexapod = device("nicos_mlz.jcns.devices.ohe.HexapodSpecial",
        description = "Hexapod special / configuration device",
        tangodevice = tango_base + "hexapodspecial/1",
        workspaces = hexapod_workspaces,
        lowlevel = True,
    ),
    omega = device("nicos_mlz.maria.devices.motor.Motor",
        description = "Hexapod base rotation table",
        tangodevice = tango_base + "hexapodbase/dt",
        unit = "deg",
        precision = 0.005,
        fmtstr = "%.3f",
        invert = True,
    ),
    detarm = device("nicos_mlz.maria.devices.motor.Motor",
        description = "Hexapod detector arm rotation",
        tangodevice = tango_base + "hexapodbase/da",
        unit = "deg",
        precision = 0.005,
        fmtstr = "%.3f",
        invert = True,
    ),
    t2t = device("nicos_mlz.maria.devices.motor.MasterSlaveMotor",
        description = "2 theta axis moving detarm = 2 * omega",
        master = "omega",
        slave = "detarm",
        scale = 2.,
    ),
    rx = device("nicos.devices.tango.Motor",
        description = "Hexapod rotation around X",
        tangodevice = tango_base + "hexapodbase/rx",
        unit = "deg",
        precision = 0.001,
        fmtstr = "%.3f",
    ),
    ry = device("nicos.devices.tango.Motor",
        description = "Hexapod rotation around Y",
        tangodevice = tango_base + "hexapodbase/ry",
        unit = "deg",
        precision = 0.001,
        fmtstr = "%.3f",
    ),
    rz = device("nicos.devices.tango.Motor",
        description = "Hexapod rotation around Z",
        tangodevice = tango_base + "hexapodbase/rz",
        unit = "deg",
        precision = 0.001,
        fmtstr = "%.3f",
    ),
    tx = device("nicos.devices.tango.Motor",
        description = "Hexapod translation in X",
        tangodevice = tango_base + "hexapodbase/tx",
        unit = "mm",
        precision = 0.01,
        fmtstr = "%.2f",
    ),
    ty = device("nicos.devices.tango.Motor",
        description = "Hexapod translation in Y",
        tangodevice = tango_base + "hexapodbase/ty",
        unit = "mm",
        precision = 0.01,
        fmtstr = "%.2f",
    ),
    tz = device("nicos.devices.tango.Motor",
        description = "Hexapod translation in Z",
        tangodevice = tango_base + "hexapodbase/tz",
        unit = "mm",
        precision = 0.01,
        fmtstr = "%.2f",
    ),
)
