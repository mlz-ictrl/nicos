description = 'Setup for the ANDOR CCD camera at BOA using the CCDWWW server'

motprefix = 'SQ:BOA:mcu1:DCCDATZ'
counterprefix = 'SQ:BOA:counter'

excludes = ['embl', 'andor']

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
        readpv = counterprefix + '.S4',
    ),
    ccdwww_connector = device('nicos_sinq.boa.devices.ccdwww.CCDWWWConnector',
        description = 'Connector for CCDWWW',
        baseurl = 'http://boaccd:8080/ccd',
        base64auth = 'xxx',
        byteorder = 'big',
    ),
    ccdwww = device('nicos_sinq.boa.devices.ccdwww.AndorCCD',
        description = 'CCDWWW image channel',
        ismaster = True,
        connector = 'ccdwww_connector',
        shape = (1024, 1024)
    ),
    ccd_cooler = device('nicos_sinq.boa.devices.ccdwww.CCDCooler',
        description = 'CCD sensor cooler',
        connector = 'ccdwww_connector',
        unit = 'state',
        fmtstr = '%s'
    ),
    andorccd = device('nicos.devices.generic.detector.Detector',
        description = 'Dummy detector to encapsulate ccdwww',
        monitors = [
            'ccdwww',
        ],
        timers = [
            'ccdwww',
        ],
        images = [
            'ccdwww',
        ],
        lowlevel = True
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
    boacontrol = device('nicos_sinq.boa.devices.ccdcontrol.BoaControlDetector',
        description = 'BOA CCD control',
        trigger = 'el737',
        slave_detectors = ['andorccd'],
        liveinterval = 5,
        minimum_rate = 0,
        rate_monitor = 'monitorval',
        elapsed_time = 'elapsedtime'
    ),
)

startupcode = '''
SetDetectors(boacontrol)
'''
