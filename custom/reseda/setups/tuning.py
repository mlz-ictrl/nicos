group = 'optional'
description = 'Reseda tunewave table support'

includes = ['selector', 'coils']

devices = dict(
    echotime = device('reseda.tuning.EchoTime',
        description = 'Echo time and tunewave table device',
        wavelength = 'selector_lambda',
        dependencies = [
            'subcoil_ps2',
        ],
        unit = 'ns',
        fmtstr = '%g'
    ),
)
