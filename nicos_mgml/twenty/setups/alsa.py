description = 'L041 room monitoring'
group = 'optional'

tango_base = 'tango://kfes11.troja.mff.cuni.cz:10000/alsa/'

devices = dict(
    T_squid_room = device('nicos.devices.entangle.Sensor',
        description = 'Temperature in the L041 room',
        tangodevice = tango_base + 'unipi/temp_room',
        pollinterval = 10,
        maxage = 50,
        ),
    T_alsa = device('nicos.devices.entangle.Sensor',
        description = 'Temperature in the ALSA machine',
        tangodevice = tango_base + 'unipi/temp1',
        pollinterval = 10,
        maxage = 50,
        ),
    )

