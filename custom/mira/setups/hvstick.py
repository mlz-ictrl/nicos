description = "high voltage stick"

devices = dict(
    HV   = device('devices.taco.VoltageSupply',
                  tacodevice = '//mirasrv/mira/fughv/voltage',
                  abslimits = (-5000, 5000)),
    HV_c = device('devices.taco.AnalogInput',
                  tacodevice = '//mirasrv/mira/fughv/current'),
)
