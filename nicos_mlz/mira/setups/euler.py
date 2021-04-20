description = 'PUMA Eulerian cradle'
group = 'optional'

includes = ['base']
excludes = ['mono1']

tango_base = 'tango://miractrl.mira.frm2:10000/mira/euler/'

devices = dict(
    co_ephi = device('nicos.devices.entangle.Sensor',
        lowlevel = True,
        tangodevice = tango_base + 'phi_coder',
        unit = 'deg',
    ),
    mo_ephi = device('nicos.devices.entangle.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'phi_motor',
        abslimits = (-355.0, 355.0),
        unit = 'deg',
    ),
    ephi = device('nicos.devices.generic.Axis',
        description = 'Eulerian cradle "phi" axis (the small circle)',
        motor = 'mo_ephi',
        coder = 'co_ephi',
        fmtstr = '%.3f',
        precision = 0.01,
    ),
    co_echi = device('nicos.devices.entangle.Sensor',
        lowlevel = True,
        tangodevice = tango_base + 'chi_coder',
        unit = 'deg',
    ),
    mo_echi = device('nicos.devices.entangle.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'chi_motor',
        abslimits = (-355.0, 355.0),
        unit = 'deg',
    ),
    echi = device('nicos.devices.generic.Axis',
        description = 'Eulerian cradle "chi" axis (the big circle)',
        motor = 'mo_echi',
        coder = 'co_echi',
        fmtstr = '%.3f',
        precision = 0.01,
        offset = -189.99926762282576,
    ),
    ec = device('nicos.devices.tas.EulerianCradle',
        description = 'Eulerian cradle abstract device to move to a given scattering plane',
        tas = 'mira',
        chi = 'echi',
        omega = 'ephi',
        cell = 'Sample',
    ),
)
