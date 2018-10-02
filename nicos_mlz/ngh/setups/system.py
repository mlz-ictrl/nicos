# -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = [],
    notifiers = ['email'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = False,
        serviceexp = 'p0',
        sample = 'Sample',
    ),
)
