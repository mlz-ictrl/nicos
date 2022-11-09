description = 'Setup for the magnets at NARZISS'

pvprefix = 'SQ:NARZISS:'

devices = dict(
    amag = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Analayzer magnet',
        readpv = pvprefix + 'AMAG:CurRBV',
        writepv = pvprefix + 'AMAG:CurSet',
        abslimits = (-10., 10.),
        window = .1,
    ),
    pmag = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Polarizer magnet',
        readpv = pvprefix + 'PMAG:CurRBV',
        writepv = pvprefix + 'PMAG:CurSet',
        abslimits = (-10., 10.),
        window = .1,
    ),
    smag = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Sample magnet',
        readpv = pvprefix + 'SMAG:CurRBV',
        abslimits = (-100., 100.),
        writepv = pvprefix + 'SMAG:CurSet',
        window = .1,
    ),
    spin = device('nicos_sinq.narziss.devices.spin.NarzissSpin',
        description = 'Spin control for NARZISS',
        pmag = 'pmag',
        pom = 'pom',
    ),
)
