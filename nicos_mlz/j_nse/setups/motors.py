description = 'main motors'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    mophi = device('nicos.devices.entangle.Motor',
        description = 'scattering angle',
        tangodevice = tango_base + 's7_motor/mophi',
        unit = 'deg',
    ),
    mopsi = device('nicos.devices.entangle.Motor',
        description = 'sample rotation',
        tangodevice = tango_base + 's7_motor/mopsi',
        unit = 'deg',
    ),
    moana = device('nicos.devices.entangle.Motor',
        description = 'analyzer position',
        tangodevice = tango_base + 's7_motor/moana',
        unit = 'mm',
    ),
    mo_z = device('nicos.devices.entangle.Motor',
        description = 'sample height',
        tangodevice = tango_base + 's7_motor/mo_z',
        unit = 'mm',
    ),
)
