description = 'x-z detector table'

group = 'lowlevel'

includes = []

nethost = 'deldaq50.del.frm2'

devices = dict(
    mo_x   = device('devices.taco.Motor',
                    lowlevel = True,
                    tacodevice = '//%s/del/table/xmot' % (nethost,),
                    unit = 'mm',
                    abslimits = (0, 792),
                    userlimits = (0, 277),
                   ),
    x      = device('devices.generic.Axis',
                    description = 'Detector table x axis',
                    motor = 'mo_x',
                    coder = 'mo_x',
                    obs = [],
                    fmtstr = '%.3f',
                    precision = 0.01,
                    abslimits = (0, 792),
                    userlimits = (0, 277),
                   ),
    mo_y   = device('devices.taco.Motor',
                    lowlevel = True,
                    tacodevice = '//%s/del/table/ymot' % (nethost,),
                    unit = 'mm',
                    abslimits = (0, 792),
                    userlimits = (0, 264.5),
                   ),
    y      = device('devices.generic.Axis',
                    description = 'Detector table y axis',
                    motor = 'mo_y',
                    coder = 'mo_y',
                    obs = [],
                    fmtstr = '%.3f',
                    precision = 0.01,
                    abslimits = (0, 792),
                    userlimits = (0, 264.5),
                   ),
)

