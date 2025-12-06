# TODO I think this file can be removed, so I am hiding it from the list to see
# if anyone complains
group = 'lowlevel'


description = 'Setup for the ANDOR CCD camera at BOA using the CCDWWW server'

excludes = ['andor', 'embl', 'fastcomtec', 'camini', 'andorccd-l']

motprefix = 'SQ:BOA:turboPmac1:DCCDATZ'
counterprefix = 'SQ:BOA:counter'

devices = dict(
    dccdatz = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
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
        readpv = counterprefix + '.S4',
    ),
    ccdwww_connector = device('nicos_sinq.boa.devices.ccdwww.CCDWWWConnector',
        description = 'Connector for CCDWWW',
        baseurl = 'http://boaccd:8080/ccd',
        base64auth = 'xxx',
        byteorder = 'big',
        comdelay = 1.,
        comtries = 5,
    ),
    ccdwww = device('nicos_sinq.boa.devices.ccdwww.AndorCCD',
        description = 'CCDWWW image channel',
        iscontroller = True,
        connector = 'ccdwww_connector',
        shape = (1024, 1024),
        pollinterval = 30,
        maxage = 30,
    ),
    ccd_cooler = device('nicos_sinq.boa.devices.ccdwww.CCDCooler',
        description = 'CCD sensor cooler',
        connector = 'ccdwww_connector',
        unit = 'state',
        pollinterval = 30,
        maxage = 30,
        fmtstr = '%s'
    ),
    cooler_temperature = device('nicos.devices.generic.paramdev.ReadonlyParamDevice',
        description = 'Actual temperature reading',
        device = 'ccd_cooler',
        parameter = 'temperature',
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
        visibility = ()
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
    boacontrol = device('nicos_sinq.boa.devices.ccdcontrol.BoaControlDetector',
        description = 'BOA CCD control',
        trigger = 'el737',
        followers = ['andorccd'],
        liveinterval = 5,
        minimum_rate = 0,
        rate_monitor = 'monitorval',
        elapsed_time = 'elapsedtime'
    ),
)

startupcode = '''
SetDetectors(boacontrol)
'''
