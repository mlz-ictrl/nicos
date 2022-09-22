description = 'LHe/LN2 Levelmeter AMI1700'

pv_root = 'SE-SEE:SE-AMILVL-001:'

devices = dict(
    levelmeter_N2=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Liquid nitrogen level',
        readpv='{}N2Monitor'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    levelmeter_He=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Liquid helium level',
        readpv='{}HeMonitor'.format(pv_root),
        pva=True,
        monitor=True,
    )
)
