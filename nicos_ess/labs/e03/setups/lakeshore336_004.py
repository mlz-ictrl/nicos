description = 'The Lakeshore 336 temperature controller.'

pv_root = 'SE-SEE:SE-LS336-004:'

devices = dict(
    ls336_004_T_A=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel A temperature',
        readpv='{}KRDG0'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    ls336_004_SP_A=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel A set-point',
        readpv='{}SETP1'.format(pv_root),
        writepv='{}SETP_S1'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    ls336_004_T_B=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel B temperature',
        readpv='{}KRDG1'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    ls336_004_SP_B=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel B set-point',
        readpv='{}SETP2'.format(pv_root),
        writepv='{}SETP_S2'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    ls336_004_T_C=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel C temperature',
        readpv='{}KRDG2'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    ls336_004_SP_C=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel C set-point',
        readpv='{}SETP3'.format(pv_root),
        writepv='{}SETP_S3'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    ls336_004_T_D=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Channel D temperature',
        readpv='{}KRDG3'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    ls336_004_SP_D=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Channel D set-point',
        readpv='{}SETP4'.format(pv_root),
        writepv='{}SETP_S4'.format(pv_root),
        pva=True,
        monitor=True,
    ),
)
