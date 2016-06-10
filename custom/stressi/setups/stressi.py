description = 'STRESS-SPEC setup'

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
    )
)
