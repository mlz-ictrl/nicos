description = 'Trigger (output on connector no 9)'

display_order = 100

devices = dict(
    #Trigger signal
    trigger = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = 3.0,
        description = 'Trigger bit',
        readpv = 'SQ:ICON:b4io3:CamTrig',
        writepv = 'SQ:ICON:b4io3:CamTrig',
        lowlevel = False,
    ),
)
