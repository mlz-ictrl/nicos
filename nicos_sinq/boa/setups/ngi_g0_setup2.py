description = 'nGI G0 devices in the SINQ ICON.'

display_order = 20

devices = dict(
    g0_tx = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'nGI Source Grating (G0) Translation X',
        motorpv = 'SQ:BOA:ngiG:g0tx',
        errormsgpv = 'SQ:BOA:ngiG:g0tx-MsgTxt',
        precision = 0.002,
    ),
    g0_rz = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'nGI Source Grating (G0) Rotation Y',
        motorpv = 'SQ:BOA:ngiG:g0ry',
        errormsgpv = 'SQ:BOA:ngiG:g0ry-MsgTxt',
        precision = 0.01,
    )
)
