description = 'FOV linear axis for the small box (100 x 100)'

group = 'optional'

excludes = ['fov_190x190', 'fov_300x300']
includes = ['frr']

devices = dict(
    fov_100_mot = device('nicos.devices.generic.VirtualMotor',
        description = 'FOV motor',
        lowlevel = True,
        abslimits = (15, 615),
        userlimits = (16, 514),
        unit = 'mm',
        speed = 5,
    ),
    fov_100_enc = device('nicos.devices.generic.VirtualCoder',
        description = 'FOV encoder',
        motor = 'fov_100_mot',
        lowlevel = True,
    ),
    fov_100 = device('nicos.devices.generic.Axis',
        description = 'FOV linear axis',
        pollinterval = 5,
        maxage = 10,
        precision = 0.1,
        fmtstr = '%.2f',
        motor = 'fov_100_mot',
        coder = 'fov_100_enc',
    ),
)
