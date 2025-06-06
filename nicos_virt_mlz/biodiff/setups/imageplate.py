description = 'Image plate detector setup'
group = 'basic'

sysconfig = dict(
    datasinks = ['TIFFFileSaver', 'LiveViewSink',],
)

includes = [
    'counter', 'shutter', 'microstep', 'reactor', 'nl1', 'astrium',
]

devices = dict(
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    TIFFFileSaver = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'Saves image data in TIFF format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
        mode = 'I;16',
    ),
    mcstas = device('nicos_virt_mlz.biodiff.devices.McStasSimulation',
        description = 'McStas simulation',
        sample = 'Sample',
        s1 = 'd_diaphragm1',
        s2 = 'd_diaphragm2',
        wavelength = 'selector_lambda',
        omega = 'omega_sampletable',
        intensityfactor = 1e20,
    ),
    imgplate = device('nicos_virt_mlz.biodiff.devices.detector.McStasImage',
        mcstas = 'mcstas',
        mcstasfile = 'PSD_BIODIFF_total.psd',
        description = 'Image plate image',
        fmtstr = '%d',
        size = (625, 450),
        visibility = (),
    ),
    imgplate_timer = device('nicos.devices.mcstas.McStasTimer',
        description='McStas virtual neutron counts timer channel',
        mcstas = 'mcstas',
        fmtstr = '%.2f',
        unit = 's',
        visibility = (),
    ),
    imgdet = device('nicos_virt_mlz.biodiff.devices.detector.Detector',
        description = 'Image plate detector',
        mcstas = 'mcstas',
        timers = ['imgplate_timer'],
        images = ['imgplate'],
        gammashutter = 'gammashutter',
        photoshutter = 'photoshutter',
    ),
)

startupcode = '''
SetDetectors(imgdet)
'''
