description = 'Setup for the ANDOR CCD camera at BOA'

# This line for the real thing...
#pvprefix = 'SQ:BOA:andor:'
# This line below for simulation, uses dchabot/simioc docker container
pvprefix = 'sim:det:'

detector_channel = 'cam1:'
motprefix = 'SQ:BOA:mcu1:DCCDATZ'
counterprefix = 'SQ:BOA:counter'

excludes = ['andorccd', 'embl']

devices = dict(
    dccdatz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Andor focus motor',
        motorpv = motprefix,
        errormsgpv = motprefix + '-MsgTxt',
    ),
    el737_preset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        epicstimeout = 3.0,
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = counterprefix + '.TP',
        presetpv = counterprefix + '.TP',
    ),
    elapsedtime = device('nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        epicstimeout = 3.0,
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = counterprefix + '.T',
    ),
    monitorpreset = device('nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        epicstimeout = 3.0,
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = counterprefix + '.PR2',
        presetpv = counterprefix + '.PR2',
    ),
    monitorval = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Monitor for neutron beam',
        type = 'monitor',
        readpv = counterprefix + '.S2',
    ),
    protoncurr = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Monitor for proton current',
        type = 'monitor',
        readpv = counterprefix + '.S5',
    ),
    el737 = device('nicos_sinq.devices.detector.SinqDetector',
        epicstimeout = 3.0,
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = counterprefix + '.CNT',
        pausepv = counterprefix + ':Pause',
        statuspv = counterprefix + ':Status',
        errormsgpv = counterprefix + ':MsgTxt',
        monitorpreset = [
            'monitorpreset',
        ],
        timepreset = ['el737_preset'],
        thresholdpv = counterprefix + ':Threshold',
        thresholdcounterpv = counterprefix + ':ThresholdCounter',
    ),
    time_preset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Acquisition time preset',
        unit = 's',
        readpv = pvprefix + detector_channel + 'AcquireTime_RBV',
        presetpv = pvprefix + detector_channel + 'AcquireTime',
    ),
    adimage_channel = device('nicos_ess.devices.epics.area_detector.ADImageChannel',
        description = 'Image data from CCD',
        pvprefix = pvprefix + 'cam1',
        readpv = pvprefix + 'image1:ArrayData',
        epicstimeout = 30.
    ),
    andor = device('nicos_sinq.devices.epics.SINQ_area_detector.AndorAreaDetector',
        epicstimeout = 3.0,
        description = 'Area detector instance for ANDOR CCD',
        unit = '',
        statepv = pvprefix + detector_channel + 'DetectorState_RBV',
        startpv = pvprefix + detector_channel + 'Acquire',
        errormsgpv = pvprefix + detector_channel + 'StatusMessage_RBV',
        timers = [
            'time_preset',
        ],
        monitors = [],
        images = ['adimage_channel'],
        liveinterval = 5,
        saveintervals = [60]
    ),
    boacontrol = device('nicos_sinq.boa.devices.ccdcontrol.BoaControlDetector',
        description = 'BOA CCD control',
        trigger = 'el737',
        followers = ['andor'],
        liveinterval = 5,
        minimum_rate = 0,
        rate_monitor = 'monitorval',
        elapsed_time = 'elapsedtime'
    ),
)

startupcode = '''
SetDetectors(boacontrol)
'''
