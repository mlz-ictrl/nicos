#  -*- coding: utf-8 -*-

description = 'detectors'

group = 'lowlevel'  # is included by panda.py

devices = dict(
    mcstas = device('nicos_virt_mlz.panda.devices.mcstas.PandaSimulation',
        description = 'McStas simulation',
    ),
    timer = device('nicos.devices.mcstas.McStasTimer',
        mcstas = 'mcstas',
        lowlevel = True,
    ),
    mon1 = device('nicos.devices.mcstas.McStasCounter',
        type = 'monitor',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_mon1.psd',
        fmtstr = '%d',
        lowlevel = True,
    ),
    mon2 = device('nicos.devices.mcstas.McStasCounter',
        type = 'monitor',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_mon2.psd',
        fmtstr = '%d',
        lowlevel = True,
    ),
    det1 = device('nicos.devices.mcstas.McStasCounter',
        type = 'counter',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_det2.psd',  # correct: in reality det1 is behind det2
        fmtstr = '%d',
        lowlevel = True,
    ),
    det2 = device('nicos.devices.mcstas.McStasCounter',
        type = 'counter',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_det1.psd',
        fmtstr = '%d',
        lowlevel = True,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'combined four channel single counter detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        counters = ['det1', 'det2'],
        images = [],
        maxage = 1,
        pollinterval = 1,
    ),
)

startupcode = '''
SetDetectors(det)
'''
