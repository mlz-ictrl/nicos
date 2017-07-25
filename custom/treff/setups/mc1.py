description = '(MC 1)'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/'
tango_s7 = tango_base + 'FZJS7/'

devices = dict(
    mc1_rot = device('nicos.devices.tango.Motor',
                     description = 'MC1 rotation motor',
                     tangodevice = tango_s7 + 'mc1_rot',
                     precision = 0.01,
                     unit = 'deg',
                    ),
    mc1_x   = device('nicos.devices.tango.Motor',
                     description = 'MC1 x motor',
                     tangodevice = tango_s7 + 'mc1_x',
                     precision = 0.01,
                     unit = 'mm',
                    ),
)
