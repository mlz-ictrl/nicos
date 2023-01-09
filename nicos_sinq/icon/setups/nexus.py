description = 'Devices for writing NeXus files'

excludes = ['detector']

sysconfig = dict(datasinks = ['nxsink', 'quiecksink', 'fits'],)

devices = dict(
    sample_pos1 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Sample Position 1',
        standard_devices = []
    ),
    sample_pos2 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Sample Position 2',
        standard_devices = []
    ),
    sample_pos3 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Sample Position 3',
        standard_devices = []
    ),
    detector_pos = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Detector position',
        standard_devices = []
    ),
    image_key = device('nicos.devices.generic.ManualSwitch',
        description = 'the type of image stored',
        states = [0, 1, 2, 3]
    ),
    image_type = device('nicos.devices.generic.Switcher',
        description = 'Changing the image type by name',
        moveable = 'image_key',
        mapping = {
            'projection': 0,
            'flat_field': 1,
            'dark_field': 2,
            'invalid': 3
        },
        precision = .1,
    ),
    pixel_size = device('nicos.devices.generic.ManualMove',
        description = 'pixel size of the detetcor',
        abslimits = (0, 5),
        unit = 'mm',
    ),
    detector_distance = device('nicos.devices.generic.ManualMove',
        description = 'Distance of detector from sample',
        abslimits = (0, 5000),
        unit = 'mm',
    ),
    lenses = device('nicos.devices.generic.ManualSwitch',
        description = 'Switch for the various camera lenses',
        states = [
            'Nikkor 50mm/1.4', 'Zeiss Macroplanar 100m/2.0',
            'Zeiss Otus 55mm/1.4'
        ]
    ),
    scintillator = device('nicos.devices.generic.ManualSwitch',
        description = 'Switch for the various scintillators',
        states = ['Gadox', '6Li:ZnF/Gadox', '6Li:ZnF']
    ),
    scintillator_thickness = device('nicos.devices.generic.ManualSwitch',
        description = 'Switch for the thickness of the scintillator',
        states = [10, 20, 30, 50, 100, 200, 300]
    ),
    nxsink = device('nicos.nexus.nexussink.NexusSink',
        description = "Sink for NeXus file writer",
        filenametemplate = ['icon%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.icon.nexus.nexus_templates.ICONTemplateProvider',
    ),
    quiecksink = device('nicos_sinq.devices.datasinks.QuieckSink',
        description = 'Sink for sending UDP datafile notifications'
    ),
    fits = device('nicos_sinq.devices.niagfitssink.NIAGFitsSink',
        description = 'Sink for FITS files',
        detectors = [
            'andor',
        ],
        filenametemplate = [
            'icon%(year)sn%(scancounter)06di%(pointcounter)08d.fits'
        ]
    ),
)
