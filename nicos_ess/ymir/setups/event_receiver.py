description = 'Event Receiver setup.'

pv_root = 'YMIR-TS:Ctrl-EVR-01:'

devices = dict(
    EVR_time=device(
        'nicos.devices.epics.EpicsStringReadable',
        description='Status of the EVR timing',
        readpv='{}Time-Valid-Sts'.format(pv_root),
        monitor=True
    ),
    EVR_link=device(
        'nicos.devices.epics.EpicsStringReadable',
        description='Status of link to EVG',
        readpv='{}Link-Sts'.format(pv_root),
        monitor=True
    ),
    NTP_DIFF=device(
        'nicos.devices.epics.EpicsReadable',
        description='The difference between the Utgård EVR and the NTP client',
        readpv='LABS-VIP:time-fs725-01:NSDiffNTPEVR',
        unit='ns',
        monitor=True
    ),
    EFU_stat=device(
        'nicos_ess.devices.efu_status.EFUStatus',
        description='EFU connection status',
        ipconfig='172.30.242.39:8011',
    ),
)
