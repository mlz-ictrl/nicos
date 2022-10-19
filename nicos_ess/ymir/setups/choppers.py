description = 'The mini-chopper for YMIR'

pv_root = 'YMIR-ChpSy1:Chop-MIC-101:'

devices = dict(
    mini_chopper_status=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The chopper status.',
        readpv='{}Chop_Stat'.format(pv_root),
        visibility=(),
    ),
    mini_chopper_control=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Used to start and stop the chopper.',
        readpv='{}Cmd'.format(pv_root),
        writepv='{}Cmd'.format(pv_root),
        requires={'level': 'admin'},
        visibility=set(),
        mapping={
            'Start chopper': 6,
            'Stop chopper': 3,
            'Reset chopper': 1,
            'Clear chopper': 8,
        },
    ),
    mini_chopper_speed=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The current speed.',
        readpv='{}Spd_Stat'.format(pv_root),
        writepv='{}Spd_SP'.format(pv_root),
        abslimits=(0.0, 14),
        monitor=True,
        precision=0.1,
    ),
    mini_chopper_delay=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The current delay.',
        readpv='{}ChopDly-S'.format(pv_root),
        writepv='{}ChopDly-S'.format(pv_root),
        abslimits=(0.0, 71428571.0),
        monitor=True,
    ),
    mini_chopper=device(
        'nicos_ess.devices.epics.chopper.EssChopperController',
        description='The mini-chopper controller',
        state='mini_chopper_status',
        command='mini_chopper_control',
    ),
)
