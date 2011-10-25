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

    PSDGas = device('nicos.io.NamedDigitalInput',
                    mapping = {0: 'empty', 1: 'okay'},
                    pollinterval = 10,
                    maxage = 30,
                    tacodevice = 'mira/io/in'),

    dtx    = device('nicos.axis.TacoAxis',
                    tacodevice = 'mira/axis/dtx',
                    abslimits = (0, 1500),
                    pollinterval = 5,
                    maxage = 10),
)
