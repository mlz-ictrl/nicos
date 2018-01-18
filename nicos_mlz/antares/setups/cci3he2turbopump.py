description = 'Turbo pump for 3He insert from FRM II Sample environment group'

nethost = 'cci3he2'

devices = {
    'cci3he2_turbopump':
        device('nicos.devices.taco.DigitalOutput',
            description = 'The 3He turbo pump',
            tacodevice = '//%s/box/module/vpump' % nethost,
            pollinterval = 5,
            maxage = 6,
        ),
}
