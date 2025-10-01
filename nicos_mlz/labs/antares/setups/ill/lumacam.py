description = 'Timepix3 Detector at ILL'

group = 'optional'

sysconfig = dict(
    datasinks = [],
)

base_pv = 'office:penguin:tpx3cam:cam1:'

devices = dict(
    det_lumacam = device('nicos_sinq.devices.epics.area_detector.EpicsAreaDetector',
        description = 'Detector',
        statepv = base_pv + 'DetectorState_RBV',
        basepv = base_pv,
        startpv = base_pv + 'Acquire'
    )
)
startupcode = """
SetDetectors(det_lumacam)
"""
