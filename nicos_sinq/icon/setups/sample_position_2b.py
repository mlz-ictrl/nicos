description = 'Sample position 2b devices in the SINQ ICON.'

display_order = 35

pvprefix = 'SQ:ICON:sp2b:'

devices = dict(
    sp2b_tx = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Sample position 2b, Translation X axis',
        motorpv = pvprefix + 'sp2b_tx',
        errormsgpv = pvprefix + 'sp2b_tx-MsgTxt',
        precision = 0.01,
        reference_direction = 'reverse'
    ),
    sp2b_ry = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Sample position 2b, Rotation Y axis',
        motorpv = pvprefix + 'sp2b_ry',
        errormsgpv = pvprefix + 'sp2b_ry-MsgTxt',
        precision = 0.01,
    ),
    sp2b_rz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Sample position 2b, Rotation Z axis',
        motorpv = pvprefix + 'sp2b_rz',
        errormsgpv = pvprefix + 'sp2b_rz-MsgTxt',
        precision = 0.01,
    )
)
