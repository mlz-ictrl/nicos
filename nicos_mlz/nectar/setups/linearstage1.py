description = 'Additional linear stage'

group = 'optional'

nethost = 'nectarsrv.nectar.frm2.tum.de'

devices = dict(
    linst1_m = device('nicos.devices.taco.Motor',
        tacodevice = '//%s/nectar/cam/fov' % nethost,
        abslimits = (0.0001,900),
        comtries = 3,
        lowlevel = True,
    ),
    linst1 = device('nicos.devices.generic.Axis',
        description = 'Free useable linear stage',
        pollinterval = 5,
        maxage = 12,
        fmtstr = '%.2f',
        userlimits = (0.0001,900),
        precision = 0.1,
        motor = 'linst1_m',
    ),
)
