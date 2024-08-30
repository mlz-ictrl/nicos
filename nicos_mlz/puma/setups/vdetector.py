description = 'common detector devices provided by McStas simulation'

group = 'lowlevel'

excludes = ['detector', 'multianalysis', 'defcal', 'polarizationkinetic']

devices = dict(
    mcstas = device('nicos_virt_mlz.puma.devices.detector.McStasSimulation',
        description = 'McStas simulation',
        tas = 'puma',
        sample = 'Sample',
        ef = 'Ef',
        ei = 'Ei',
        primary_collimation = 'alpha1',
        neutronspersec = {
            'localhost': 2.2e6,
            'taco6.ictrl.frm2.tum.de': 2.2e6,
            'ictrl23': 2.55e6,
            configdata('config_data.host'): 1.3e6,
        },
    ),
    timer = device('nicos.devices.mcstas.McStasTimer',
        mcstas = 'mcstas',
        visibility = (),
    ),
    mon1 = device('nicos_virt_mlz.puma.devices.detector.Counter',
        type = 'monitor',
        mcstas = 'mcstas',
        description = 'Monitor 1',
        mcstasfile = 'PostMono_Monitor.dat',
        visibility = (),
        fmtstr = '%d',
    ),
    det1 = device('nicos_virt_mlz.puma.devices.detector.Counter',
        type = 'counter',
        mcstas = 'mcstas',
        mcstasfile = 'Detector1.dat',
        fmtstr = '%d',
        visibility = (),
    ),
    det2 = device('nicos_virt_mlz.puma.devices.detector.Counter',
        type = 'counter',
        mcstas = 'mcstas',
        mcstasfile = 'Detector2.dat',
        fmtstr = '%d',
        visibility = (),
    ),
    det3 = device('nicos_virt_mlz.puma.devices.detector.Counter',
        type = 'counter',
        mcstas = 'mcstas',
        mcstasfile = 'Detector3.dat',
        fmtstr = '%d',
        visibility = (),
    ),
    det = device('nicos.devices.mcstas.Detector',
        description = 'Puma detector device (3 counters)',
        mcstas = 'mcstas',
        timers = ['timer'],
        monitors = ['mon1'],
        counters = ['det1', 'det2', 'det3'],
        images = [],
        maxage = 1,
        pollinterval = 1,
    ),
)

startupcode = '''
SetDetectors(det)
'''
