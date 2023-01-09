description = 'Setup for the Simulation AD camera'

# This line for the real thing...
#pvprefix = 'SQ:CAM:andor:'
# This line below for simulation, uses dchabot/simioc docker container
pvprefix = 'sim:det:'

detector_channel = 'cam1:'

excludes = ['detector', 'andor', 'detector_phys']
includes = ['beam_monitor']

# For the multiple detector NeXus file writing to work, the ADImageChannel must have
# a name <setup-name>_image, for example simad_image

devices = dict(
    time_preset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Acquisition time preset',
        unit = 's',
        readpv = pvprefix + detector_channel + 'AcquireTime_RBV',
        presetpv = pvprefix + detector_channel + 'AcquireTime',
    ),
    simad_image = device('nicos_sinq.devices.epics.area_detector.ADImageChannel',
        description = 'Image data from CCD',
        pvprefix = pvprefix + 'cam1',
        readpv = pvprefix + 'image1:ArrayData',
        epicstimeout = 30.
    ),
    andor = device('nicos_sinq.devices.epics.area_detector.EpicsAreaDetector',
        description = 'Area detector instance for Sim AD',
        unit = '',
        statepv = pvprefix + detector_channel + 'DetectorState_RBV',
        startpv = pvprefix + detector_channel + 'Acquire',
        errormsgpv = pvprefix + detector_channel + 'StatusMessage_RBV',
        timers = [
            'time_preset',
        ],
        monitors = [],
        images = ['simad_image'],
        liveinterval = 5,
        saveintervals = [60],
        basepv = pvprefix + detector_channel,
    ),
    exp_ok = device('nicos_sinq.devices.epics.EpicsReadable',
        description = 'Exposure sufficient',
        readpv = 'SQ:ICON:sumi:EXPOK',
    ),
    camera = device('nicos_sinq.devices.ccdcontrol.NIAGControl',
        description = 'Count control for NIAG CCD detectors',
        trigger = 'andor',
        followers = ['oracle'],
        rate_monitor = 'oracle',
        rate_threshold = 'exp_threshold',
        exp_ok = 'exp_ok',
    ),
)

startupcode = '''
SetDetectors(camera)
'''
