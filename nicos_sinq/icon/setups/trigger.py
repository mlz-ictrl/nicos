description = 'Trigger (output on connector no 9)'

display_order = 100

devices = dict(
    #Trigger signal
    trigger = device('nicos.devices.epics.EpicsDigitalMoveable',
        description = 'Trigger bit',
        readpv = 'SQ:ICON:b4io3:CamTrig',
        writepv = 'SQ:ICON:b4io3:CamTrig',
    ),
)
