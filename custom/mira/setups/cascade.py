name = 'cascade psd detector'

includes = ['detector']

devices = dict(
    psd    = device('nicos.mira.cascade.CascadeDetector',
                    subdir = 'cascade',
                    server = 'miracascade.mira.frm2:1234',
                    slave = True,
                    master = 'det'),

    PSDHV  = device('nicos.mira.iseg.IsegHV',
                    tacodevice = 'mira/network/rs12_4',
                    abslimits = (-3000, 0),
                    pollinterval = 10,
                    maxage = 20,
                    channel = 1,
                    unit = 'V',
                    fmtstr = '%d'),

    PSDGas = device('nicos.taco.NamedDigitalInput',
                    mapping = {0: 'empty', 1: 'okay'},
                    pollinterval = 10,
                    maxage = 30,
                    tacodevice = 'mira/io/psdgas'),

    dtx    = device('nicos.taco.Axis',
                    tacodevice = 'mira/axis/dtx',
                    abslimits = (0, 1500),
                    pollinterval = 5,
                    maxage = 10),

    # this overwrites the "det" device from the detector setup
    # and removes all counters
    #det    = device('nicos.detector.FRMDetector',
    #                t  = 'timer',
    #                m1 = 'mon1',
    #                m2 = 'mon2',
    #                m3 = None,
    #                z1 = None,
    #                z2 = None,
    #                z3 = None,
    #                z4 = None,
    #                z5 = None,
    #                fmtstr = 'timer %s, mon1 %s, mon2 %s',
    #                maxage = 2,
    #                pollinterval = 0.5),
)
