description = '(MC 2)'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/FZJS7/'

devices = dict(
    mc2_rot = device('nicos.devices.tango.Motor',
        description = 'MC2 rotation motor',
        tangodevice = tango_base + 'mc2_rot',
        precision = 0.01,
        unit = 'deg',
    ),
)
