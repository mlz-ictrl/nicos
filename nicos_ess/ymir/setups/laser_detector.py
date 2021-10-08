description = 'The laser detector in the YMIR cave'

devices = dict(
    laser_pv=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The laser PV',
        readpv='plc-ts:PLC:slowdata',
        lowlevel=True,
        epicstimeout=3.0,
    ),
    laser=device('nicos_ess.ymir.devices.laser_detector.LaserDetector',
        description='Laser detector in YMIR cave',
        laser='laser_pv'
    ),
)
