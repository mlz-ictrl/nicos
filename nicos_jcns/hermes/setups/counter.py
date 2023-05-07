description = 'HERMES timer and counter channels'
group = 'optional'
display_order = 5

tango_base = 'tango://phys.hermes.jcns.fz-juelich.de:10000/hermes/'

sysconfig = dict(datasinks = ['n110_imagesink'])

devices = dict(
    timer = device('nicos.devices.entangle.TimerChannel',
        description = 'JCNS counter card timer.',
        tangodevice = tango_base + 'jcns_counter/timer',
    ),
    counter0 = device('nicos.devices.entangle.CounterChannel',
        description = 'JCNS counter card channel 0.',
        tangodevice = tango_base + 'jcns_counter/channel0',
        type = 'counter',
    ),
    counter1 = device('nicos.devices.entangle.CounterChannel',
        description = 'JCNS counter card channel 1.',
        tangodevice = tango_base + 'jcns_counter/channel1',
        type = 'counter',
    ),
    counter2 = device('nicos.devices.entangle.CounterChannel',
        description = 'JCNS counter card channel 2.',
        tangodevice = tango_base + 'jcns_counter/channel2',
        type = 'counter',
    ),
    counter3 = device('nicos.devices.entangle.CounterChannel',
        description = 'JCNS counter card channel 3.',
        tangodevice = tango_base + 'jcns_counter/channel3',
        type = 'counter',
    ),
    counter4 = device('nicos.devices.entangle.CounterChannel',
        description = 'JCNS counter card channel 4.',
        tangodevice = tango_base + 'jcns_counter/channel4',
        type = 'counter',
    ),
    tofcounter = device('nicos_jcns.hermes.devices.n110_counter.TOFChannel',
        description = 'N110 counter card with 5 time-of-flight channels.',
        tangodevice = tango_base + 'n110_counter/tof_channel',
    ),
    tofcounter_rate = device('nicos.devices.generic.RateChannel',
        description = 'Full N110 counts and rate',
    ),
    tofcounter_roirate = device('nicos.devices.generic.RateRectROIChannel',
        description = 'N110 counts and rate in region of interest.',
    ),
    counters = device('nicos.devices.generic.detector.Detector',
        description = 'HERMES counter channels.',
        counters = ['counter0', 'counter1', 'counter2', 'counter3',
                    'counter4', 'tofcounter_rate', 'tofcounter_roirate'],
        images = ['tofcounter'],
        timers = ['timer'],
        postprocess = [('tofcounter_rate', 'tofcounter', 'timer'),
                       ('tofcounter_roirate', 'tofcounter', 'timer')],
    ),
    n110_imagesink = device('nicos_jcns.hermes.devices.n110_counter.ImageSink',
        description = 'Saves image data provided by the N110 TOF counter card '
        'in a text file.',
        filenametemplate = [
            '%(Exp.users)s_%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s.n110',
        ],
        detectors = ['counters'],
    ),
)

startupcode = '''
AddDetector(counters)
'''
