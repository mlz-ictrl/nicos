description = 'Event Receiver setup.'

pv_root = 'Utg-Ymir:TS-EVR-01:'

devices = dict(
    EVR_time=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        readpv='{}Time-Valid-Sts'.format(pv_root),
        description='Status of the EVR timing',
        monitor=True),
    EVR_link=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        readpv='{}Link-Sts'.format(pv_root),
        description='Status of link to EVG',
        monitor=True),
    NTP_DIFF=device(
        'nicos.devices.epics.pva.EpicsReadable',
        readpv='LABS-VIP:time-fs725-01:NSDiffNTPEVR'.format(pv_root),
        unit='ns',
        description='The difference between the Utgård EVR and the NTP client',
        monitor=True),

)
