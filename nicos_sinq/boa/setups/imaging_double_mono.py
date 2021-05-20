description = 'Double crystal monochromator at ICON.'

display_order = 20

excludes = [
    'double_mono',
]

devices = dict(
    mth1 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Double cristal monochromator, Theta 1',
        motorpv = 'SQ:ICON:dcm:mth1',
        errormsgpv = 'SQ:ICON:dcm:mth1-MsgTxt',
        precision = 0.01,
        reference_direction = 'reverse',
    ),
    mth2 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Double cristal monochromator, Theta 2',
        motorpv = 'SQ:ICON:dcm:mth2',
        errormsgpv = 'SQ:ICON:dcm:mth2-MsgTxt',
        precision = 0.01,
        reference_direction = 'reverse',
    ),
    mtz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Double cristal monochromator, translation Z',
        motorpv = 'SQ:ICON:dcm:mtz',
        errormsgpv = 'SQ:ICON:dcm:mtz-MsgTxt',
        precision = 0.01,
        reference_direction = 'reverse',
    ),
    dcm_lambda = device('nicos_sinq.devices.doublemono.DoubleMonochromator',
        description = 'ICON double cristal monochromator',
        unit = 'Angstroem',
        safe_position = 0.,
        dvalue = 3.335,
        distance = 60.,
        abslimits = (1.1, 6.2),
        mth1 = 'mth1',
        mth2 = 'mth2',
        mtx = 'mtz'
    ),
)
