description = 'Polarizer device.'

devices = dict(
    uty = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Analyser y motor',
        motorpv = 'SQ:MORPHEUS:mota:uty',
        errormsgpv = 'SQ:MORPHEUS:mota:uty-MsgTxt',
    ),
    utz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Analyser z motor',
        motorpv = 'SQ:MORPHEUS:mota:utz',
        errormsgpv = 'SQ:MORPHEUS:mota:utz-MsgTxt',
    ),
    po2 = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Analyser rotation',
        motorpv = 'SQ:MORPHEUS:motb:po2',
        errormsgpv = 'SQ:MORPHEUS:motb:po2-MsgTxt',
    ),
    ispin = device('nicos_sinq.morpheus.devices.ispin_morpheus.MorpheusSpin',
        description = 'Incident polarization controlling the spin-flipper,'
        ' can be used for scans '
        '(0 = spin-up / 1 = spin-down)',
        magnet_c = 'pfc',
        magnet_f = 'pff',
        su_c = -1.2,
        su_f = -0.7,
    ),
)
