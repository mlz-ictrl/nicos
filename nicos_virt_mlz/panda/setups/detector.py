description = 'detectors'
group = 'lowlevel'  # is included by panda.py

devices = dict(
    mcstas = device('nicos_virt_mlz.panda.devices.mcstas.PandaSimulation',
        description = 'McStas simulation',
    ),
    timer = device('nicos.devices.mcstas.McStasTimer',
        mcstas = 'mcstas',
        visibility = (),
    ),
    mon1 = device('nicos.devices.mcstas.McStasCounter',
        type = 'monitor',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_mon1.psd',
        fmtstr = '%d',
        visibility = (),
    ),
    mon2 = device('nicos.devices.mcstas.McStasCounter',
        type = 'monitor',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_mon2.psd',
        fmtstr = '%d',
        visibility = (),
    ),
    det1 = device('nicos.devices.mcstas.McStasCounter',
        type = 'counter',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_det2.psd',  # correct: in reality det1 is behind det2
        fmtstr = '%d',
        visibility = (),
    ),
    det2 = device('nicos.devices.mcstas.McStasCounter',
        type = 'counter',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_det1.psd',
        fmtstr = '%d',
        visibility = (),
    ),
    det = device('nicos.devices.mcstas.Detector',
        description = 'combined four channel single counter detector',
        mcstas = 'mcstas',
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
