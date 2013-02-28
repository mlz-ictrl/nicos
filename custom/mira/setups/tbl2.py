description = 'Huber rotation tables'

group = 'optional'

devices = dict(
    tbl2    = device('devices.taco.Motor',
                       lowlevel = False,
                       tacodevice = 'mira/rot/tbl2',
                       abslimits = (-360, 360),
                       resetcall = 'deviceReset'),
)
