description = 'Analyzer device'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/FZJS7/'

devices = dict(
    analyzer_tilt = device('nicos.devices.tango.Motor',
        description = 'Analyzer tilt',
        tangodevice = tango_base + 'analyzer_tilt',
        precision = 0.01,
        fmtstr = '%.3f',
        unit = 'deg',
    ),
)
