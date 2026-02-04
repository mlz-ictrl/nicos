description = 'Extra linear axis in the SINQ ICON.'

display_order = 35

pvprefix = 'SQ:ICON:sp2b:'

devices = dict(
    extra_linear_axis = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample position 2b, extra linear axis',
        motorpv = pvprefix + 'sp2b_tx2',
        errormsgpv = pvprefix + 'sp2b_tx2-MsgTxt',
        precision = 0.01,
    ),
)
