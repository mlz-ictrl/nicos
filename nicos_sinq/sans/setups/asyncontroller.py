description = 'Initialisation for asyn controllers for directly speaking to hardware'

group = 'lowlevel'

devices = dict(
    port14 = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the devices connected to serial 14',
        commandpv = 'SQ:SANS:p14' + '.AOUT',
        replypv = 'SQ:SANS:p14' + '.AINP',
    ),
)
