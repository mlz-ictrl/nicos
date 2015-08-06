description = 'FRM II 7.5 T superconducting magnet'

group = 'optional'

includes = ['alias_B', 'alias_sth']

# Important: nethost != setupname
nethost = 'magnet'

devices = {
    'B_%s' % setupname: device('devices.taco.CurrentSupply',
                               description = 'The magnetic field',
                               tacodevice = '//%s/magnet/smc120/t' % nethost,
                               abslimits = (-7.5, 7.5),
                              ),

    'sth_%s' % setupname: device('devices.taco.Axis',
                                 description = 'Cryotstat tube rotation',
                                 tacodevice = '//%s/magnet/axis/tube' % nethost,
                                 abslimits = (-180, 180),
                                ),
}

# Maximum temeratures for field operation above 80A (6.6T) taken from the manual
maxtemps = [None, 4.3, 4.3, 5.1, 4.7, None, None, None, 4.3]

for i in range(1, 9):
    dev = device('devices.taco.TemperatureSensor',
                 description = '7.5T magnet temperature sensor %d' % i,
                 tacodevice = '//%s/magnet/ls218/sens%d' % (nethost, i),
                 warnlimits = (0, maxtemps[i]),
                 pollinterval = 30,
                 maxage = 90,
                 unit = 'K',
                )
    devices['%s_T%d' % (setupname, i)] = dev

alias_config = [
    ('B', 'B_%s' % setupname, 100),
    ('sth', 'sth_%s' % setupname, 100),
]
