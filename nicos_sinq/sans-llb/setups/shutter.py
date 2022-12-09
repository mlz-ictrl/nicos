description = 'Devices for the shutter at SANS-LLB'

spsprefix = 'SQ:SANS-LLB:SPS:'
hide = True

devices = dict(
    shbutton = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = 3.0,
        description = 'Shutter button',
        readpv = spsprefix + 'SHUTTER_BUTTON',
        writepv = spsprefix + 'SHUTTER_BUTTON',
        visibility = (),
    ),
    shpulse = device('nicos.devices.generic.Pulse',
        description = 'pulse for activating shutter',
        moveable = 'shbutton',
        onvalue = 1,
        offvalue = 0,
        ontime = .1,
        visibility = (),
    ),
    shutter = device('nicos_sinq.devices.s7_switch.S7Shutter',
        description = 'Shutter Control',
        button = 'shpulse',
        readpv = spsprefix + 'SHUTTER_OPEN_RBV',
        closedpv = spsprefix + 'SHUTTER_CLOSED_RBV',
        readypv = spsprefix + 'SHUTTER_READY_RBV',
        errorpv = spsprefix + 'SHUTTER_ERROR_RBV',
        timeout = 5,
    ),
)
