description = 'Huber rotation tables'

group = 'optional'

devices = dict(
    tbl2    = device('devices.tango.Motor',
                     description = 'second general-use rotator table',
                     tangodevice = 'tango://mira1.mira.frm2:10000/mira/table/rot2',
                     abslimits = (-360, 360),
                     precision = 0.05,
                    ),
)
