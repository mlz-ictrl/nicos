description = 'Initialisation for asyn controllers for directly speaking to hardware'

devices = dict(
    port14 = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Controller of the devices connected to serial 14',
        commandpv = 'SQ:SANS:tiwi' + '.AOUT',
        replypv = 'SQ:SANS:tiwi' + '.AINP',
    ),
    mcu1 = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Controller of the devices connected to serial 14',
        commandpv = 'SQ:SANS:mcu1' + '.AOUT',
        replypv = 'SQ:SANS:mcu1' + '.AINP',
    ),
)
