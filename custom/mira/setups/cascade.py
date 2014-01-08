description = 'SANS mode with PSD detector'
group = 'basic'

includes = ['detector', 'mono2']

devices = dict(
    psd_padformat = device('mira.cascade.CascadePadRAWFormat',
                           lowlevel = True),
    psd_tofformat = device('mira.cascade.CascadeTofRAWFormat',
                           lowlevel = True),
    psd_xmlformat = device('mira.cascade.MiraXMLFormat',
                           master = 'det',
                           sampledet = 'sampledet',
                           mono = 'mono',
                           lowlevel = True),

    psd    = device('mira.cascade.CascadeDetector',
                    description = 'CASCADE detector',
                    subdir = 'cascade',
                    server = 'miracascade.mira.frm2:1234',
                    slave = True,
                    master = 'det',
                    fileformats = ['psd_padformat', 'psd_tofformat',
                                   'psd_xmlformat']),

    PSDHV  = device('devices.vendor.iseg.IsegHV',
                    description = 'High voltage supply for the CASCADE detector (usually -2850 V)',
                    tacodevice = '//mirasrv/mira/network/rs12_4',
                    abslimits = (-3000, 0),
                    warnlimits = (-3000, -2800),
                    pollinterval = 10,
                    maxage = 20,
                    channel = 1,
                    unit = 'V',
                    fmtstr = '%d'),

    PSDGas = device('devices.taco.NamedDigitalInput',
                    description = 'Sensor to indicate low pressure in counting gas of CASCADE',
                    mapping = {'empty': 0, 'okay': 1},
                    warnlimits = ('okay', 'okay'),
                    pollinterval = 10,
                    maxage = 30,
                    tacodevice = '//mirasrv/mira/io/psdgas'),

    dtx    = device('mira.axis.PhytronAxis',
                    description = 'Detector translation along the beam on Franke table',
                    tacodevice = '//mirasrv/mira/axis/dtx',
                    abslimits = (0, 1490),
                    pollinterval = 5,
                    maxage = 10),

    sampledet = device('devices.generic.ManualMove',
                       description = 'Sample-detector distance to be written to the data files',
                       abslimits = (0, 5000),
                       unit = 'mm'),
)
