description = 'cascade psd detector'

includes = ['detector', 'mono2']

devices = dict(
    psd    = device('nicos.mira.cascade.CascadeDetector',
                    subdir = 'cascade',
                    server = 'miracascade.mira.frm2:1234',
                    slave = True,
                    master = 'det',
                    sampledet = 'sampledet',
                    mono = 'mono'),

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

    sampledet = device('nicos.generic.ManualMove',
                       abslimits = (0, 5000),
                       unit = 'mm'),
)
