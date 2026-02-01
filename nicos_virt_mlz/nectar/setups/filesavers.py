description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'nxsink', 'DiObSink'],
)

devices = dict(
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
    ),
    nxsink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.templates.TomoTemplateProvider',
        filenametemplate = ['nectar%(scancounter)07d.nxs'],
        settypes = {'scan', 'point'},  # 'subscan', },
        filemode = 0o440,
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
