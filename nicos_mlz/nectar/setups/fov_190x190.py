description = 'FOV linear axis for the medium box (190 x 190)'

group = 'optional'

excludes = ['fov_100x100', 'fov_300x300']

tango_base = 'tango://phytron01.nectar.frm2:10000/'

devices = dict(
    fov_190_mot = device('nicos.devices.tango.Motor',
        description = 'FOV motor',
        tangodevice = tango_base + 'box/FOV/mot',
        lowlevel = True,
        abslimits = (159, 670),
        userlimits = (160, 669),
    ),
    fov_190_enc = device('nicos.devices.tango.Sensor',
        description = 'FOV encoder',
        tangodevice = tango_base + 'box/FOV/enc',
        lowlevel = True,
    ),
    fov_190 = device('nicos.devices.generic.Axis',
        description = 'FOV linear axis',
        pollinterval = 5,
        maxage = 10,
        precision = 0.1,
        fmtstr = '%.2f',
        motor = 'fov_190_mot',
        coder = 'fov_190_enc',
    ),
)
