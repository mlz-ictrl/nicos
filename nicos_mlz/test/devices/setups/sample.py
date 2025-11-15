sysconfig = dict(
    experiment = 'Exp',
)

devices = dict(
    Exp = device('nicos.devices.experiment.Experiment',
        sample = 'Sample',
        elog = True,
        dataroot = '',  # path.join(runtime_root, 'data'),
        propprefix = 'p',
        templates = '',   # path.join(module_root, 'test', 'script_templates'),
        zipdata = True,
    ),
    Sample = device('nicos_mlz.devices.sample.Sample'),
    tsample = device('nicos_mlz.devices.sample.TASSample'),
)
