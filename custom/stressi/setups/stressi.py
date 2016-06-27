description = 'STRESS-SPEC setup with sample table'

group = 'basic'

includes = ['system', 'sampletable', 'monochromator', 'detector',
            'primaryslit', 'slits', ]

servername = 'VME'

nameservice = 'stressictrl'

devices = dict(
    mux = device('devices.vendor.caress.MUX',
                 description = 'The famous MUX',
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'MUX3 38 4 ttyS1 1',
                 lowlevel = True,
                ),
    wav = device('devices.generic.manual.ManualMove',
                 description = 'The incoming wavelength',
                 fmtstr = '%.1f',
                 default = 1.7,
                 unit = 'AA',
                 abslimits = (0.9, 2.5),
                ),
)
