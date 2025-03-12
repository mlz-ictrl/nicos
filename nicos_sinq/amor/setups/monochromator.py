description = 'Monochromator devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

devices = dict(
    mom=device('nicos_sinq.devices.epics.motor.SinqMotor',
               epicstimeout=3.0,
               description='Tilt monochromator motor',
               motorpv=pvprefix + 'mom',
               ),
    moz=device('nicos_sinq.devices.epics.motor.SinqMotor',
               epicstimeout=3.0,
               description='Monochromator z position of rotation axis motor',
               motorpv=pvprefix + 'moz',
               ),
    mtz=device('nicos_sinq.devices.epics.motor.SinqMotor',
               epicstimeout=3.0,
               description='Monochromator z position relative to rotation axis motor',
               motorpv=pvprefix + 'mtz',
               ),
    mty=device('nicos_sinq.devices.epics.motor.SinqMotor',
               epicstimeout=3.0,
               description='Monochromator y position motor',
               motorpv=pvprefix + 'mty',
               ),
    m2t = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical motor monochromator two theta',
        motortype = 'm2t',
        controller = 'controller_lm'
    ),
)
