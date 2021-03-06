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
    rx = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation around X',
        tangodevice = hexapod + 'rx',
        unit = 'deg',
        precision = 0.001,
        fmtstr = '%.3f',
    ),
    ry = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation around Y',
        tangodevice = hexapod + 'ry',
        unit = 'deg',
        precision = 0.001,
        fmtstr = '%.3f',
    ),
    rz = device('nicos.devices.tango.Motor',
        description = 'Hexapod rotation around Z',
        tangodevice = hexapod + 'rz',
        unit = 'deg',
        precision = 0.001,
        fmtstr = '%.3f',
    ),
    tx = device('nicos.devices.tango.Motor',
        description = 'Hexapod translation in X',
        tangodevice = hexapod + 'tx',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    ty = device('nicos.devices.tango.Motor',
        description = 'Hexapod translation in Y',
        tangodevice = hexapod + 'ty',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    tz = device('nicos.devices.tango.Motor',
        description = 'Hexapod translation in Z',
        tangodevice = hexapod + 'tz',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
)
