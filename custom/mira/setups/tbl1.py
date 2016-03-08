description = 'Huber rotation tables'

group = 'optional'

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    tbl1    = device('devices.tango.Motor',
                     description = 'first general-use rotator table',
                     tangodevice = tango_base + 'table/rot1',
                     abslimits = (-360, 360),
                     precision = 0.05,
                    ),
)
