description = 'Polariser devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

includes = ['logical_motors']

devices = dict(
    mom=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Tilt monochromator motor',
               motorpv=pvprefix + 'mom',
               errormsgpv=pvprefix + 'mom-MsgTxt',
               ),
    moz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Monochromator z position of rotation axis motor',
               motorpv=pvprefix + 'moz',
               errormsgpv=pvprefix + 'moz-MsgTxt',
               ),
    mtz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Monochromator z position relative to rotation axis motor',
               motorpv=pvprefix + 'mtz',
               errormsgpv=pvprefix + 'mtz-MsgTxt',
               ),
    mty=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Monochromator y position motor',
               motorpv=pvprefix + 'mty',
               errormsgpv=pvprefix + 'mty-MsgTxt',
               ),
    m2t = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical motor monochromator two theta',
        motortype = 'm2t',
        controller = 'controller_lm'
    ),
)
