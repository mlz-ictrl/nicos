description = 'x-z detector table at beam TREFF with the short x axis'

group = 'lowlevel'

excludes = ['long_table_treff', 'table_lab']

nethost = 'localhost'

devices = dict(
    mo_x = device('nicos.devices.taco.Motor',
        lowlevel = True,
        tacodevice = '//%s/del/table/xmot' % (nethost,),
        unit = 'mm',
        abslimits = (0, 277),
        userlimits = (0, 277),
    ),
    x = device('nicos.devices.generic.Axis',
        description = 'Detector table x axis',
        motor = 'mo_x',
        coder = 'mo_x',
        obs = [],
        fmtstr = '%.3f',
        precision = 0.01,
        abslimits = (0, 277),
        userlimits = (0, 277),
    ),
    mo_y = device('nicos.devices.taco.Motor',
        lowlevel = True,
        tacodevice = '//%s/del/table/ymot' % (nethost,),
        unit = 'mm',
        abslimits = (0, 264.5),
        userlimits = (0, 264.5),
    ),
    y = device('nicos.devices.generic.Axis',
        description = 'Detector table y axis',
        motor = 'mo_y',
        coder = 'mo_y',
        obs = [],
        fmtstr = '%.3f',
        precision = 0.01,
        abslimits = (0, 264.5),
        userlimits = (0, 264.5),
    ),
)
