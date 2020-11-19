description = 'Camera focusing at position 2 - MIDI box'

group = 'lowlevel'

display_order = 45

pvprefix = 'SQ:ICON:midi:'

devices = dict(
    focus_midi = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Camera focus midi box',
        motorpv = pvprefix + 'cmid',
        errormsgpv = pvprefix + 'cmid-MsgTxt',
        precision = 0.01,
    ),
)
