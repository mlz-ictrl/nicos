description = 'Setup for the ANDOR CCD camera at BOA'

pvprefix = 'KM36:sim:'

detector_channel = 'cam1:'
motprefix = 'SQ:BOA:turboPmac1:DCCDATZ'
counterprefix = 'SQ:BOA:counter'

excludes = ['andorccd', 'embl', 'andorccd-l', 'andor', 'fastcomtec', 'camini']

devices = dict(
    dccdatz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Andor focus motor',
        motorpv = motprefix,
    ),
    el737_preset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = counterprefix + '.TP',
        presetpv = counterprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = counterprefix + '.T',
    ),
    monitorpreset = device('nicos_sinq.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = counterprefix + '.PR2',
        presetpv = counterprefix + '.PR2',
    ),
    monitorval = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for neutron beam',
        type = 'monitor',
        readpv = counterprefix + '.S2',
    ),
    protoncurr = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for proton current',
        type = 'monitor',
        readpv = counterprefix + '.S5',
    ),
    el737 = device('nicos_sinq.devices.detector.SinqDetector',
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
    time_preset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Acquisition time preset',
        unit = 's',
        readpv = pvprefix + detector_channel + 'AcquireTime_RBV',
        presetpv = pvprefix + detector_channel + 'AcquireTime',
    ),
    adimage_channel = device('nicos_sinq.devices.epics.area_detector.ADImageChannel',
        description = 'Image data from CCD',
        pvprefix = pvprefix + 'cam1',
        readpv = pvprefix + 'image1:ArrayData',
        epicstimeout = 30.
    ),
    andor = device('nicos_sinq.devices.epics.area_detector.EpicsAreaDetector',
        description = 'Area detector instance for sim AD',
        unit = '',
        basepv = pvprefix + detector_channel,
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
