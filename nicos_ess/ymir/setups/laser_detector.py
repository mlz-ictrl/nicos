description = 'The laser detector in the YMIR cave'

devices = dict(
    laser_pv=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='The laser PV',
        readpv='YMIR-SETS:SE-BADC-001:SLOWDATA',
        visibility=(),
    ),
    laser_timing_status=device(
        'nicos_ess.ymir.devices.laser_detector.TimingStatusDevice',
        description='The lasers timestamps synchronisation status',
        readpv='YMIR-SETS:SE-BPTP-001:PTP_STATUS',
        visibility=(),
    ),
    laser=device(
        'nicos_ess.ymir.devices.laser_detector.LaserDetector',
        description='Laser detector in YMIR cave',
        laser='laser_pv',
        timingstatus='laser_timing_status',
    ),
)
