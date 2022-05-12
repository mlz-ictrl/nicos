description = 'The Lakeshore 336 temperature controller.'

pv_root = 'SE-SEE:SE-LS336-004:'

devices = dict(
    T_ls336_A_001=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel A temperature',
        readpv='{}KRDG0'.format(pv_root),
        writepv='{}SETP_S1'.format(pv_root),
        targetpv='{}SETP1'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    S_ls336_A_001=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel A raw sensor reading',
        readpv='{}SRDG0'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    T_ls336_B_001=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel B temperature',
        readpv='{}KRDG1'.format(pv_root),
        writepv='{}SETP_S2'.format(pv_root),
        targetpv='{}SETP2'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    S_ls336_B_001=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel B raw sensor reading',
        readpv='{}SRDG1'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    T_ls336_C_001=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel C temperature',
        readpv='{}KRDG2'.format(pv_root),
        writepv='{}SETP_S3'.format(pv_root),
        targetpv='{}SETP3'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    S_ls336_C_001=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel C raw sensor reading',
        readpv='{}SRDG2'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
    T_ls336_D_001=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel D temperature',
        readpv='{}KRDG3'.format(pv_root),
        writepv='{}SETP_S4'.format(pv_root),
        targetpv='{}SETP4'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    S_ls336_D_001=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel D raw sensor reading',
        readpv='{}SRDG3'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
    ),
)
