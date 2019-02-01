description = 'GP2 Camera'
pvprefix = 'TE:NDW1958:GP2:'

devices = dict(
    experimental = device('nicos_ess.devices.epics.extensions.EpicsMappedMoveable',
                     description = 'Start/Stop collecting data',
                     readpv = pvprefix + 'COMMAND',
                     writepv = pvprefix + 'COMMAND:SP',
                     mapping = {'Stop': 0, 'Experimental': 1},
                     ),

    filepath = device('nicos.devices.epics.EpicsStringMoveable',
                      description = 'Full path of file to write data to',
                      readpv = pvprefix + 'FILEPATH',
                      writepv = pvprefix + 'FILEPATH:SP',
                      ),
)

