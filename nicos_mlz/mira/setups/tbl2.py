description = 'Huber rotation tables'

group = 'optional'

tango_base = 'tango://miractrl.mira.frm2:10000/mira/'

devices = dict(
    tbl2 = device('nicos.devices.entangle.Motor',
        description = 'second general-use rotator table',
        tangodevice = tango_base + 'table/rot2',
        abslimits = (-360, 360),
        precision = 0.05,
    ),
)
