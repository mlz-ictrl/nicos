description = 'Simulation for a second detector on the simulation AD'

# This  uses  a dchabot/simioc docker container for a simulation AD
pvprefix = 'sim:det:'
detector_channel = 'cam1:'

sysconfig = dict(datasinks = ['fits2'],)

excludes = ['detector']

# For the multiple detector NeXus file writing to work, the ADImageChannel must have
# a name <setup-name>_image, for example simad_image

devices = dict(
    time_preset2 = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Acquisition time preset',
        unit = 's',
        readpv = pvprefix + detector_channel + 'AcquireTime_RBV',
        presetpv = pvprefix + detector_channel + 'AcquireTime',
    ),
    simad2_image = device('nicos_sinq.devices.epics.area_detector.ADImageChannel',
        description = 'Image data from CCD',
        pvprefix = pvprefix + 'cam1',
        readpv = pvprefix + 'image1:ArrayData',
        epicstimeout = 30.
    ),
    cam2 = device('nicos_sinq.devices.epics.area_detector.EpicsAreaDetector',
        description = 'Simulation of a second detector on Sim AD',
        unit = '',
        statepv = pvprefix + detector_channel + 'DetectorState_RBV',
        startpv = pvprefix + detector_channel + 'Acquire',
        errormsgpv = pvprefix + detector_channel + 'StatusMessage_RBV',
        timers = [
            'time_preset2',
        ],
        monitors = [],
        images = ['simad2_image'],
        liveinterval = 5,
        saveintervals = [60],
        basepv = pvprefix + detector_channel,
    ),
    fits2 = device('nicos_sinq.devices.niagfitssink.NIAGFitsSink',
        description = 'Sink for FITS files',
        detectors = [
            'cam2',
        ],
        filenametemplate = [
            'icon%(year)sn%(scancounter)06dx%(pointcounter)08d.fits'
        ]
    ),
)
