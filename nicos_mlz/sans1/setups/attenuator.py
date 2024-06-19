description = 'attenuator'

#includes = ['system']

#excludes = ['collimation_config']

# included by sans1
group = 'lowlevel'

# IP-adresse: 172.25.49.107
tango_base = 'tango://hw.sans1.frm2.tum.de:10000/col/col-1/'

devices = dict(
    att = device('nicos_mlz.sans1.devices.collimotor.Switcher',
        description = 'Attenuator',
        mapping = dict(dia10=15.626, x10=108.626, x100=201.626, x1000=294.626, open=387.626),
        moveable = 'att_a',
        blockingmove = False,
        pollinterval = 15,
        maxage = 60,
        precision = 0.1,
        fmtstr = '%s',
    ),
    att_a = device('nicos.devices.generic.Axis',
        description = 'Attenuator axis',
        motor = 'att_m',
        coder = 'att_c',
        dragerror = 17,
        precision = 0.05,
        visibility = (),
        jitter = 1,
    ),
    att_m = device('nicos.devices.entangle.Motor',
        description = 'Attenuator motor',
        tangodevice = tango_base + 'att_mot',
        unit = 'mm',
        abslimits = (-400, 600),
        visibility = (),
        precision = 0.0025,
    ),
    att_c = device('nicos.devices.entangle.Sensor',
        description = 'Attenuator coder',
        tangodevice = tango_base + 'att_enc',
        unit = 'mm',
        visibility = (),
    ),
)
