from os import path

from test.utils import cache_addr, runtime_root

name = 'CAMEA setup to test NeXus templates'


sysconfig = dict(
    cache = cache_addr,
    experiment = 'Exp',
    instrument = 'CAMEA',
    datasinks = [],
    notifiers = [],
)

devices = dict(
    Sample = device('nicos.devices.sample.Sample'),
    CAMEA = device(
        'test.nicos_sinq.camea.test_template_provider.MockInstrument',
        description = 'instrument object',
        instrument = 'SINQ CAMEA',
        responsible = '',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/camea/',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = path.join(runtime_root, 'data'),
        serviceexp = 'Service',
        sample = 'Sample',
    ),
)
