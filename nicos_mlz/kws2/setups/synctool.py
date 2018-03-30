description = 'Chopper ext. synchronization multiplier'

group = 'optional'

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    Synctool = device('nicos.devices.tango.DigitalOutput',
        description = 'Multiplier/divider for external synchronization pulse',
        tangodevice = tango_base + 'synctool/value',
    ),
)
