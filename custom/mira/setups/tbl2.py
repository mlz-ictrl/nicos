description = 'Huber rotation tables'

group = 'optional'

devices = dict(
    tbl2    = device('devices.taco.Motor',
                     description = 'second general-use rotator table',
                     tacodevice = '//mirasrv/mira/rot/tbl2',
                     abslimits = (-360, 360),
                     resetcall = 'deviceInit',
                    ),
)
