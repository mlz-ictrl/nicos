description = 'NL2a shutter'
group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    nl2a = device(
        'nicos.devices.entangle.NamedDigitalOutput',
        description = 'NL2a shutter',
        mapping = {'closed': 0, 'open': 1},
        tangodevice = tango_base + 's7_io/shutter',
        pollinterval = 60,
        maxage = 120,
    ),
)
