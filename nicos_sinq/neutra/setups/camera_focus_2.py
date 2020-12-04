description = 'Camera Focusing Midibox'

pvprefix = 'SQ:NEUTRA:board4:'

group = 'lowlevel'

display_order = 40
epics_timeout = 3.0

devices = dict(
    focus_midi_axis = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = epics_timeout,
        description = 'Axis Camera Positioning Midibox',
        motorpv = pvprefix + 'CMID',
        errormsgpv = pvprefix + 'CMID-MsgTxt',
        precision = 0.01,
        lowlevel = True,
    ),
    focus_midi_brake = device('nicos.devices.epics.EpicsDigitalMoveable',
        epicstimeout = epics_timeout,
        readpv = 'SQ:NEUTRA:b4io4:BrakeCMID',
        writepv = 'SQ:NEUTRA:b4io4:BrakeCMID',
        lowlevel = True,
    ),
    focus_midi = device('nicos.devices.generic.sequence.LockedDevice',
        description = 'Sample Positioning Measuringposition 2 Z with brake',
        device = 'focus_midi_axis',
        lock = 'focus_midi_brake',
        unlockvalue = 1,
        lockvalue = 0,
        unit = 'mm',
    )
)
