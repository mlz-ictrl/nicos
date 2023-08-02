description = 'Camera Focusing Midibox'

pvprefix = 'SQ:NEUTRA:board4:'

group = 'lowlevel'

display_order = 40

devices = dict(
    focus_midi_axis = device('nicos.devices.epics.pyepics.motor.HomingProtectedEpicsMotor',
        description = 'Axis Camera Positioning Midibox',
        motorpv = pvprefix + 'CMID',
        errormsgpv = pvprefix + 'CMID-MsgTxt',
        precision = 0.01,
        visibility = set(),
    ),
    focus_midi_brake = device('nicos.devices.epics.pyepics.EpicsDigitalMoveable',
        readpv = 'SQ:NEUTRA:b4io4:BrakeCMID',
        writepv = 'SQ:NEUTRA:b4io4:BrakeCMID',
        visibility = set(),
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
