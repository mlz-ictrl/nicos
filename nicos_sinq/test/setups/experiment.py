description = 'system setup'
from os import path
from test.utils import runtime_root

sysconfig = dict(
    experiment = 'Exp',
    instrument = 'Instr',
)

devices = dict(
    Sample = device('nicos.devices.tas.TASSample'),
    Exp = device('nicos_sinq.devices.experiment.Experiment',
        description = 'experiment object',
        sample = 'Sample',
        instrument = "SINQ TEST",
        dataroot = path.join(runtime_root, 'data'),
        forcescandata = True,
    ),
    Instr = device('nicos.devices.instrument.Instrument',
        instrument = 'INSTR',
        responsible = 'R. Esponsible <r.esponsible@web.test>',
        operators = ['NICOS developer team'],
    ),
    SinqExp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        sample = 'Sample',
        instrument = "SINQ TEST-Legacy",
        dataroot = path.join(runtime_root, 'data'),
        forcescandata = True,
    ),
)
