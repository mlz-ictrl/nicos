description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'nxsink', 'DiObSink'],
)

devices = dict(
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
        filemode = 0o440,
    ),
    nxsink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.templates.TomoTemplateProvider',
        filenametemplate = ['tomo%(scancounter)07d.nxs'],
        settypes = {'scan', 'point'},  # 'subscan', },
        filemode = 0o440,
        device_mapping = dict(stx='stx_huber', sty='sty_huber'),
    ),
    image_key = device('nicos.devices.generic.ManualSwitch',
        visibility = {'metadata', },
        states = [0, 1, 2],
        fmtstr = '%d',
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink',
        settypes = {'point', },
    ),
)

startupcode="""
AddEnvironment('image_key')
"""
