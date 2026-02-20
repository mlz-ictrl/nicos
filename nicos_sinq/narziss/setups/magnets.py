description = 'Setup for the magnets at NARZISS'

pvprefix = 'SQ:NARZISS:'

devices = dict(
    amag = device('nicos.devices.epics.base.EpicsAnalogMoveable',
        description = 'Analayzer magnet',
        monitor = True,
        writepv = pvprefix + 'AMAG:CurSet',
        readpv = pvprefix + 'AMAG:CurSet',
        precision = .1,
    ),
    pmag = device('nicos.devices.epics.base.EpicsAnalogMoveable',
        description = 'Polarizer magnet',
        monitor = True,
        writepv = pvprefix + 'PMAG:CurSet',
        readpv = pvprefix + 'PMAG:CurSet',
        precision = .1,
    ),
    smag = device('nicos.devices.epics.base.EpicsAnalogMoveable',
        description = 'Sample magnet',
        monitor = True,
        writepv = pvprefix + 'SMAG:CurSet',
        readpv = pvprefix + 'SMAG:CurSet',
        precision = .1,
    ),
    spin = device('nicos_sinq.narziss.devices.spin.NarzissSpin',
        description = 'Spin control for NARZISS',
        pmag = 'pmag',
        pom = 'pom',
    ),
)
