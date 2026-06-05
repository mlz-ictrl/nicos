description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'nxsink_s', 'nxsink_p', 'DiObSink'],
)

devices = dict(
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
        filemode = 0o440,
    ),
    nxsink_s = device('nicos_mlz.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.templates.TomoTemplateProvider',
        filenametemplate = ['%(scancounter)07d.nxs'],
        settypes = {'scan'},  # 'subscan', },
        filemode = 0o440,
        device_mapping = dict(stx='stx', sty='sty'),
    ),
    nxsink_p = device('nicos_mlz.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.templates.TomoTemplateProvider',
        filenametemplate = ['%(pointcounter)07d.nxs'],
        settypes = {'point'},  # 'subscan', },
        filemode = 0o440,
        device_mapping = dict(stx='stx', sty='sty'),
    ),
    image_key = device('nicos.devices.generic.ManualSwitch',
        visibility = {'metadata', },
        states = [0, 1, 2],
        fmtstr = '%d',
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink',
        description = 'Updates di/ob links',
    ),
)
