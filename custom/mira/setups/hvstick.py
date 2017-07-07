description = "high voltage stick"

devices = dict(
    HV   = device('nicos.devices.taco.VoltageSupply',
                  description = 'voltage on the HV stick',
                  tacodevice = '//mirasrv/mira/fughv/voltage',
                  abslimits = (-5000, 5000),
                 ),
    HV_c = device('nicos.devices.taco.AnalogInput',
                  lowlevel = True,
                  tacodevice = '//mirasrv/mira/fughv/current',
                 ),
)
