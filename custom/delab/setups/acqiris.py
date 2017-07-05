description = 'acqiris detector'

group = 'optional'

excludes = ['qmesydaq']

includes = []

acqiris_config = (
    'TIMEBASE: Time_div: 100.0e-6  MaxSample: 10000 Delay: -500.0e-6',
    'CHANNEL: 1  FullScale:  5.0  Offset: -2.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
    'CHANNEL: 2  FullScale:  5.0  Offset: -2.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
    'CHANNEL: 3  FullScale:  5.0  Offset: -2.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
    'CHANNEL: 4  FullScale:  5.0  Offset: -2.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
    'CHANNEL: 5  FullScale:  5.0  Offset: -2.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
    'CHANNEL: 6  FullScale:  0.2  Offset: -0.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
    'TRIGGER: Internal trigCoupling: DC slope: Positive level1: 0.042 level2: 0.0 trigger_class: EDGE',
    'CHANNEL: 7  FullScale:  5.0  Offset: -2.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
    'CHANNEL: 8  FullScale:  5.0  Offset: -2.0  Coupling: DC_50Ohm Bandwidth: No_Limit',
)

devices = dict(
    tim = device('nicos_mlz.delab.devices.acqiris.Timer',
                 description = 'The timer device',
                 nameserver = 'deldaq50.del.frm2',
                 counterfile = '/home/caress/acqiris/data/runid.txt',
                 objname = 'acqirishzb',
                 ismaster = False,
                ),
    det1 = device('nicos_mlz.delab.devices.acqiris.Counter',
                  description = 'The counter device',
                  nameserver = 'deldaq50.del.frm2',
                  type = 'counter',
                  counterfile = '/home/caress/acqiris/data/runid.txt',
                  runnumber = 123456,
                  objname = 'acqirishzb',
                  ismaster = True,
                  config = '\n'.join(acqiris_config),
                 ),
    acqiris = device('nicos.devices.generic.Detector',
                     description = 'Acqiris card',
                     timers  = ['tim'],
                     monitors = [],
                     counters = ['det1'],
                     fmtstr = 'timer %s, cnt %s',
                     maxage = 2,
                     pollinterval = 0.5,
                    ),
)

startupcode = '''
SetDetectors(acqiris)
'''
