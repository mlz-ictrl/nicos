description = 'Inputs from the Pilz control box'

group = 'lowlevel'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/modbus/'

# TODO: Mapping and description of the devices

devices = dict(
    iatt1 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'iatt1',
    ),
    iatt2 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'iatt2',
    ),
    ishutter = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'ishutter',
    ),
    door = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'door',
    ),
    irc = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'irc',
    ),
    eatt1 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'eatt1',
    ),
    eatt2 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'eatt2',
    ),
    eatt3 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Unknown',
        tangodevice = tango_base + 'eatt3',
    ),
)
