description = 'FOV linear axis for the large box (300 x 300)'

group = 'optional'

excludes = ['fov_100x100', 'fov_190x190']
includes = ['frr']

devices = dict(
    fov_300_mot = device('nicos.devices.generic.VirtualReferenceMotor',
        description = 'FOV motor',
        lowlevel = True,
        abslimits = (275, 950),
        userlimits = (276, 949),
        refswitch = 'low',
        refpos = 275,
        unit = 'mm',
        speed = 5,
    ),
    # fov_300_enc = device('nicos.devices.generic.VirtualCoder',
    #     description = 'FOV encoder',
    #     motor = 'fov_300_mot',
    #     lowlevel = True,
    # ),
    fov_300 = device('nicos.devices.generic.Axis',
        description = 'FOV linear axis',
        pollinterval = 5,
        maxage = 10,
        precision = 0.1,
        fmtstr = '%.2f',
        motor = 'fov_300_mot',
        # coder = 'fov_300_enc',
    ),
)
