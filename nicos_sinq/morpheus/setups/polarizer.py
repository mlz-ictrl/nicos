description = 'Polarizer device.'

devices = dict(
    uty = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Polarizer y motor',
        motorpv = 'SQ:MORPHEUS:mota:uty',
        errormsgpv = 'SQ:MORPHEUS:mota:uty-MsgTxt',
    ),
    utz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Polarizer z motor',
        motorpv = 'SQ:MORPHEUS:mota:utz',
        errormsgpv = 'SQ:MORPHEUS:mota:utz-MsgTxt',
    ),
)
