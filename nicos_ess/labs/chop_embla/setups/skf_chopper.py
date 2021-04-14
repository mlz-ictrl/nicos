description = 'Some kind of SKF chopper'

pv_root = 'LabS-Embla:Chop-Drv-0601:'

devices = dict(
    ls155_mode=device('nicos_ess.devices.epics.pva.EpicsReadable',
        description='Drive temperature',
        readpv='{}DrvTmp_Stat'.format(pv_root),
    ),
)
