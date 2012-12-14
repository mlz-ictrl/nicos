description = 'Huber rotation tables'

group = 'optional'

devices = dict(
    table1    = device('devices.taco.Motor',
                       lowlevel = False,
                       tacodevice = 'mira/rot/tbl1',
                       abslimits = (-360, 360),
                       resetcall = 'deviceReset'),
)
