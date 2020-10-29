description = 'x-z detector table at beam TREFF with the short x axis'

group = 'lowlevel'

excludes = ['long_table_treff', 'table_lab']

tango_base = 'tango://localhost:10000/del/table/'

devices = dict(
    mo_x = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'xmot',
        unit = 'mm',
        abslimits = (0, 277),
        userlimits = (0, 277),
    ),
    x = device('nicos.devices.generic.Axis',
        description = 'Detector table x axis',
        motor = 'mo_x',
        fmtstr = '%.3f',
        precision = 0.01,
    ),
    mo_y = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'ymot',
        unit = 'mm',
        abslimits = (0, 264.5),
        userlimits = (0, 264.5),
    ),
    y = device('nicos.devices.generic.Axis',
        description = 'Detector table y axis',
        motor = 'mo_y',
        fmtstr = '%.3f',
        precision = 0.01,
    ),
)
