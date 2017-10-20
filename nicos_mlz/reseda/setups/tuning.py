group = 'optional'
description = 'Reseda tunewave table support'

includes = ['selector', 'coils']

packs = ['0a', '0b', '1']

devices = dict(
    echotime = device('nicos_mlz.reseda.devices.tuning.EchoTime',
        description = 'Echo time and tunewave table device',
        wavelength = 'selector_lambda',
        dependencies = ['gf%i' % i for i in range(5)]
            + ['hsf_%s' % entry for entry in packs]
            + ['sf_%s' % entry for entry in packs]
            + ['hrf0', 'hrf1']
            + ['nse0', 'nse1'],
        unit = 'ns',
        fmtstr = '%g'
    ),
)
