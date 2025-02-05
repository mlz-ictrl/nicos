description = 'K6221 bus devices'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    busk6221 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k6221/io',
        loglevel = 'info',
        visibility = (),
    ),
)
