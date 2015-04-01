description = 'Huber rotation tables'

group = 'optional'

devices = dict(
    tbl1    = device('devices.tango.Motor',
                     description = 'first general-use rotator table',
                     tangodevice = 'tango://mira1.mira.frm2:10000/mira/table/rot1',
                     abslimits = (-360, 360),
                     precision = 0.05,
                    ),
)
