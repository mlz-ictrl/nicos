sysconfig = dict(
    experiment = 'Exp',
)

devices = dict(
    Sample = device('nicos_sinq.amor.devices.sample.AmorSample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos_sinq.amor.devices.experiment.AmorExperiment',
                 description = 'experiment object',
                 dataroot = 'dummy',
                 scriptroot = '/dummy',
                 sample = 'Sample',
    ),
)
