description = 'Cryogenics Helium Level Meter'
group = 'lowlevel'

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    magnet_lhl = device('nicos.devices.entangle.Sensor',
        description = 'Liquid Helium Level meter',
        tangodevice = tango_base + 'sms/heliumlevel',
        pollinterval = 10,
        maxage = 60,
    ),

)
