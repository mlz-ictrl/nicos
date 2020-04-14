description = 'Event Receiver setup.'

pv_root = 'LabS-Utgard-VIP'

devices = dict(
    EVR_time = device('nicos_ess.devices.epics.base.EpicsStringReadableEss',
                readpv = '{}Time:Valid-Sts'.format(pv_root),
                description='Status of the EVR timing'),
    EVR_link = device('nicos_ess.devices.epics.base.EpicsStringReadableEss',
                readpv = '{}Link-Sts'.format(pv_root),
                description='Status of link to EVG'),
)
