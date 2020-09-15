description = 'Turbo pump for 3He insert from FRM II Sample environment group'

tango_base = "tango://cci3he02:10000/box/"

devices = {
    'cci3he02_turbopump':
        device('nicos.devices.tango.DigitalOutput',
            description = 'The 3He turbo pump',
            tangodevice = tango_base + 'i7000/turbopump',
            pollinterval = 5,
            maxage = 6,
        ),
}
