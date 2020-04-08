description = 'x-z detector table in the kiosk'

group = 'lowlevel'

nethost = 'localhost'

devices = dict(
    mo_x = device('nicos.devices.taco.Motor',
        lowlevel = True,
        tacodevice = '//%s/del/table/xmot' % (nethost,),
        unit = 'mm',
        abslimits = (0, 972),
        userlimits = (0, 972),
    ),
    x = device('nicos.devices.generic.Axis',
        description = 'Detector table x axis',
        motor = 'mo_x',
        fmtstr = '%.3f',
        precision = 0.01,
    ),
    mo_y = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = (0, 264.5),
        userlimits = (0, 264.5),
        fmtstr = '%.3f',
        jitter = 0.01,
        speed = 2.5,
        unit = 'mm',
    ),
    y = device('nicos.devices.generic.Axis',
        description = 'Detector table y axis',
        motor = 'mo_y',
        fmtstr = '%.3f',
        precision = 0.01,
    ),
)
