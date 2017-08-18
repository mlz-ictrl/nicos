description = 'Asyn serial controllers in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:serial'

devices = dict(
    serial1=device(
        'nicos_sinq.amor.devices.epics_extensions.EpicsAsynController',
        epicstimeout=3.0,
        description='Controller of the devices connected to serial 1',
        commandpv=pvprefix + '1.AOUT',
        replypv=pvprefix + '1.AINP',
    ),
    serial2=device(
        'nicos_sinq.amor.devices.epics_extensions.EpicsAsynController',
        epicstimeout=3.0,
        description='Controller of the devices connected to serial 2',
        commandpv=pvprefix + '2.AOUT',
        replypv=pvprefix + '2.AINP',
    ),
    serial3=device(
        'nicos_sinq.amor.devices.epics_extensions.EpicsAsynController',
        epicstimeout=3.0,
        description='Controller of the devices connected to serial 3',
        commandpv=pvprefix + '3.AOUT',
        replypv=pvprefix + '3.AINP',
    ),
    cter1=device(
        'nicos_sinq.amor.devices.epics_extensions.EpicsAsynController',
        epicstimeout=3.0,
        description='Controller of the counter box',
        commandpv='SQ:AMOR:cter1.AOUT',
        replypv='SQ:AMOR:cter1.AINP',
    ),
)
