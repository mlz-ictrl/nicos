description = 'Asyn serial controllers at SINQ HRPT.'

pvprefix = 'SQ:HRPT:serial'

devices = dict(
    mota = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the devices connected to serial 1',
        commandpv = pvprefix + '1.AOUT',
        replypv = pvprefix + '1.AINP',
    ),
    motb = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the devices connected to serial 2',
        commandpv = pvprefix + '2.AOUT',
        replypv = pvprefix + '2.AINP',
    ),
    motc = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the devices connected to serial 3',
        commandpv = pvprefix + '3.AOUT',
        replypv = pvprefix + '3.AINP',
    ),
    motd = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the devices connected to serial 3',
        commandpv = pvprefix + '4.AOUT',
        replypv = pvprefix + '4.AINP',
    ),
    cter1 = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the counter box',
        commandpv = 'SQ:HRPT:cter1.AOUT',
        replypv = 'SQ:HRPT:cter1.AINP',
    ),
)

modules = ['nicos_sinq.hrpt.commands.hrptcommands']
