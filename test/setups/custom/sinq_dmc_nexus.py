from os import path
from test.utils import cache_addr, runtime_root

name = 'DMC test system setup'
# This setup is called "stdsystem" so that it is not loaded automatically
# on every loadSetup.

sysconfig = dict(
    cache = cache_addr,
    experiment = 'Exp',
    instrument = 'Instr',
    datasinks = [],
    notifiers = [],
)

devices = dict(
    Sample = device('nicos.devices.sample.Sample'),
    DMC = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ DMC',
        responsible = 'Lukas Keller <lukas.keller@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/dmc/',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = path.join(runtime_root, 'data'),
        sendmail = False,
        serviceexp = 'Service',
        sample = 'Sample',
    ),
)
