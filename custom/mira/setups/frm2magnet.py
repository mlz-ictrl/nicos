description = 'FRM II 7.5 T superconducting magnet'
group = 'optional'

devices = dict(
    B        = device('devices.taco.CurrentSupply',
                      tacodevice = '//magnet.mira.frm2/magnet/smc120/t',
                      abslimits = (-5.0, 5.0),
                      ),
)

for i in range(1, 9):
    devices['Tm%d' % i] = device('devices.taco.TemperatureSensor',
                                 tacodevice = '//magnet/magnet/ls218/sens%d' % i,
                                 pollinterval = 5,
                                 )
