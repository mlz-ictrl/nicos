description = 'Setup for the magnets at NARZISS'

pvprefix = 'SQ:NARZISS:'

devices = dict(
    amag = device('nicos_ess.devices.epics.base.EpicsAnalogMoveableEss',
        epicstimeout = 3.0,
        description = 'Analayzer magnet',
        readpv = pvprefix + 'AMAG:CurRBV',
        writepv = pvprefix + 'AMAG:CurSet',
        abslimits = (-10., 10.)
    ),
    pmag = device('nicos_ess.devices.epics.base.EpicsAnalogMoveableEss',
        epicstimeout = 3.0,
        description = 'Polarizer magnet',
        readpv = pvprefix + 'PMAG:CurRBV',
        writepv = pvprefix + 'PMAG:CurSet',
        abslimits = (-10., 10.)
    ),
    smag = device('nicos_ess.devices.epics.base.EpicsAnalogMoveableEss',
        epicstimeout = 3.0,
        description = 'Sample magnet',
        readpv = pvprefix + 'SMAG:CurRBV',
        abslimits = (-10., 10.),
        writepv = pvprefix + 'SMAG:CurSet',
    ),
    spin = device('nicos_sinq.narziss.devices.spin.NarzissSpin',
        description = 'Spin control for NARZISS',
        pmag = 'pmag',
        pom = 'pom',
    ),
)
