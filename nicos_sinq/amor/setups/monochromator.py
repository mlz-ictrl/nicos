description = 'Monochromator devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

includes = ['logical_motors']

devices = dict(
    mom = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Tilt monochromator motor',
        motorpv = pvprefix + 'mom',
        errormsgpv = pvprefix + 'mom-MsgTxt',
    ),
    moz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Monochromator z position of rotation axis motor',
        motorpv = pvprefix + 'moz',
        errormsgpv = pvprefix + 'moz-MsgTxt',
    ),
    mtz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Monochromator z position relative to rotation axis motor',
        motorpv = pvprefix + 'mtz',
        errormsgpv = pvprefix + 'mtz-MsgTxt',
    ),
    mty = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Monochromator y position motor',
        motorpv = pvprefix + 'mty',
        errormsgpv = pvprefix + 'mty-MsgTxt',
    ),
)
