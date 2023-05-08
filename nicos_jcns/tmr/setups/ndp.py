description = 'Neutron depth profiling detector setup at TMR'
group = 'plugplay'

sysconfig = dict(
    datasinks = ['LiveViewSink', 'NPGZFileSink', 'YAMLFileSink'],
)

tango_base = 'tango://phys.tmr.jcns.fz-juelich.de:10000/ndp/'

filename_base = '%(proposal)s_%(session.experiment.sample.filename)s_'
scanfile_base = filename_base + '%(scancounter)08d_%(pointnumber)08d'
countfile_base = filename_base + '%(pointpropcounter)010d'

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'Virtual NDP timer channel.',
        visibility = (),
    ),
    chn1 = device('nicos_mlz.jcns.devices.detector.NDPRateImageChannel',
        description = 'NDP detector 1.',
        tangodevice = tango_base + 'fastcomtec/chn1',
        timer = 'timer',
    ),
    chn2 = device('nicos_mlz.jcns.devices.detector.NDPRateImageChannel',
        description = 'NDP detector 2.',
        tangodevice = tango_base + 'fastcomtec/chn2',
        timer = 'timer',
    ),
    chn3 = device('nicos_mlz.jcns.devices.detector.NDPRateImageChannel',
        description = 'NDP detector 3.',
        tangodevice = tango_base + 'fastcomtec/chn3',
        timer = 'timer',
    ),
    chn4 = device('nicos_mlz.jcns.devices.detector.NDPRateImageChannel',
        description = 'NDP detector 4.',
        tangodevice = tango_base + 'fastcomtec/chn4',
        timer = 'timer',
    ),
    ndpdet = device('nicos.devices.generic.detector.Detector',
        description = 'NDP detector.',
        images = ['chn1', 'chn2', 'chn3', 'chn4'],
        liveinterval = 1.,
    ),
    NPGZFileSink = device('nicos.devices.datasinks.text.NPGZFileSink',
        description = 'Saves image data in numpy text format.',
        filenametemplate = [scanfile_base + '.gz', countfile_base + '.gz'],
    ),
    YAMLFileSink = device('nicos_mlz.maria.devices.yamlformat.YAMLFileSink',
        description = 'Saves image data in YAML format.',
        filenametemplate = [scanfile_base + '.yaml', countfile_base + '.yaml'],
    ),
    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget.',
    ),
)

startupcode = '''
AddDetector(ndpdet)
'''
