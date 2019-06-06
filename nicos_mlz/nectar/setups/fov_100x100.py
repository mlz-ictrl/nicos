description = 'FOV linear axis for the small box (100 x 100)'

group = 'optional'

excludes = ['fov_190x190', 'fov_300x300']

tango_base = 'tango://phytron01.nectar.frm2:10000/'

devices = dict(
    fov_100_mot = device('nicos.devices.tango.Motor',
        description = 'FOV motor',
        tangodevice = tango_base + 'box/FOV/mot',
        lowlevel = True,
        abslimits = (15, 615),
        userlimits = (16, 514),
    ),
    fov_100_enc = device('nicos.devices.tango.Sensor',
        description = 'FOV encoder',
        tangodevice = tango_base + 'box/FOV/enc',
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
