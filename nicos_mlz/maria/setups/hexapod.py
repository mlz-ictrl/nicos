# -*- coding: utf-8 -*-

description = 'Hexapod control'
group = 'optional'

excludes = []

tango_base = 'tango://phys.maria.frm2:10000/maria/'
hexapod = tango_base + 'hexapod/h_'

devices = dict(
   detarm = device('nicos.devices.tango.Motor',
        description = 'Hexapod detector arm',
        tangodevice = hexapod + 'detarm',
        unit = 'deg',
        precision = 0.005,
        fmtstr = '%.3f',
    ),
    omega = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation table',
        tangodevice = hexapod + 'omega',
        unit = 'deg',
        precision = 0.005,
        fmtstr = '%.3f',
    ),
    t2t = device("nicos_mlz.jcns.devices.motor.MasterSlaveMotor",
        description = "2 theta axis moving detarm = 2 * omega",
        master = "omega",
        slave = "detarm",
        scale = 2.,
    ),
    rx = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy hexapod axis',
        unit = 'deg',
        abslimits = (-10, 10),
    ),
    ry = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy hexapod axis',
        unit = 'deg',
        abslimits = (-10, 10),
    ),
    rz = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy hexapod axis',
        unit = 'deg',
        abslimits = (-10, 10),
    ),
    tx = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy hexapod axis',
        unit = 'mm',
        abslimits = (-75, 75),
    ),
    ty = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy hexapod axis',
        unit = 'mm',
        abslimits = (-45, 45),
    ),
    tz = device('nicos.devices.generic.VirtualMotor',
        description = 'Dummy hexapod axis',
        unit = 'mm',
        abslimits = (-100, 100),
    ),
)
