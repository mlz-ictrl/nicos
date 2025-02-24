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
        templateclass = 'nicos_mlz.nectar.nexus.nexus_templates.TomoTemplateProvider',
        filenametemplate = ['%(scancounter)07d.nxs'],
        settypes = {'scan', 'point'},  # 'subscan', },
        filemode = 0o440,
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink',
        description = 'Updates di/ob links',
    ),
)
