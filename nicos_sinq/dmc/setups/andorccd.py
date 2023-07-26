description = 'Setup for the ANDOR CCD camera at DMC using the CCDWWW server without counter box'

excludes = ['detector']

devices = dict(
    ccdwww_connector = device('nicos_sinq.boa.devices.ccdwww.CCDWWWConnector',
        description = 'Connector for CCDWWW',
        baseurl = 'http://mpc2704:8080/ccd',
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
        pollinterval = None,
        maxage = 30,
    ),
    ccd_cooler = device('nicos_sinq.boa.devices.ccdwww.CCDCooler',
        description = 'CCD sensor cooler',
        connector = 'ccdwww_connector',
        unit = 'state',
        pollinterval = None,
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
        visibility = (),
    ),
)

startupcode = '''
SetDetectors(andorccd)
'''
