description = 'Setup for the ANDOR CCD IKON-L camera'

group = 'basic'

includes = [
    'el737',
]

excludes = [
    'andor',
]

motprefix = 'SQ:BOA:turboPmac1:DCCDATZ'

sysconfig = dict(datasinks = ['livesink'])

devices = dict(
    dccdatz = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Andor focus motor',
        motorpv = motprefix,
    ),
    ccdwww_connector = device('nicos_sinq.boa.devices.ccdwww.CCDWWWConnector',
        description = 'Connector for CCDWWW',
        baseurl = 'http://pc16783:8080/ccd',
        base64auth = 'xxx',
        byteorder = 'big',
        comdelay = 1.,
        comtries = 5,
    ),
    ccdwwwl = device('nicos_sinq.boa.devices.ccdwww.AndorCCD',
        description = 'CCDWWW image channel',
        iscontroller = True,
        connector = 'ccdwww_connector',
        shape = (2048, 2048),
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
            'ccdwwwl',
        ],
        timers = [
            'ccdwwwl',
        ],
        images = [
            'ccdwwwl',
        ],
        visibility = ()
    ),

    # Detector Device
    el737 = device('nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Nicos Detector Device',
        timers = ['elapsedtime'],
        monitors = ['hardware_preset', 'monitorval', 'protoncurr'],
        visibility = {'metadata', 'namespace'},
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

    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
)

startupcode = '''
SetDetectors(boacontrol)
'''
