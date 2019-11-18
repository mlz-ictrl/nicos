description = 'FOV linear axis for the large box (300 x 300)'

group = 'optional'

excludes = ['fov_100x100', 'fov_190x190']
includes = ['frr']

tango_base = 'tango://phytron01.nectar.frm2:10000/'

devices = dict(
    fov_300_mot = device('nicos.devices.tango.Motor',
        description = 'FOV motor',
        tangodevice = tango_base + 'box/FOV/mot',
        lowlevel = True,
        abslimits = (275, 950),
        userlimits = (276, 949),
    ),
    fov_300_enc = device('nicos.devices.tango.Sensor',
        description = 'FOV encoder',
        tangodevice = tango_base + 'box/FOV/enc',
        lowlevel = True,
    ),
    fov_300 = device('nicos.devices.generic.Axis',
        description = 'FOV linear axis',
        pollinterval = 5,
        maxage = 10,
        precision = 0.1,
        fmtstr = '%.2f',
        motor = 'fov_300_mot',
        coder = 'fov_300_enc',
    ),
)
