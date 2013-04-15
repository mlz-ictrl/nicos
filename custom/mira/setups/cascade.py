description = 'SANS mode with PSD detector'
group = 'basic'

includes = ['detector', 'mono2']

devices = dict(
    psd    = device('mira.cascade.CascadeDetector',
                    subdir = 'cascade',
                    server = 'miracascade.mira.frm2:1234',
                    slave = True,
                    master = 'det',
                    sampledet = 'sampledet',
                    mono = 'mono'),

    PSDHV  = device('devices.vendor.iseg.IsegHV',
                    tacodevice = 'mira/network/rs12_4',
                    abslimits = (-3000, 0),
                    warnlimits = (-3000, -2800),
                    pollinterval = 10,
                    maxage = 20,
                    channel = 1,
                    unit = 'V',
                    fmtstr = '%d'),

    PSDGas = device('devices.taco.NamedDigitalInput',
                    mapping = {'empty': 0, 'okay': 1},
                    warnlimits = ('okay', 'okay'),
                    pollinterval = 10,
                    maxage = 30,
                    tacodevice = 'mira/io/psdgas'),

    dtx    = device('mira.axis.PhytronAxis',
                    tacodevice = 'mira/axis/dtx',
                    abslimits = (0, 1490),
                    pollinterval = 5,
                    maxage = 10),

    sampledet = device('devices.generic.ManualMove',
                       abslimits = (0, 5000),
                       unit = 'mm'),
)
