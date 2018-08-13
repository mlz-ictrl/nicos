description = 'Polarizer devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

includes = ['distances']

devices = dict(
    pby=device('nicos_sinq.amor.devices.epics_amor_magnet.EpicsAmorMagnet',
               epicstimeout=3.0,
               description='Polarizer magnet',
               basepv='SQ:AMOR:PBY',
               pvdelim=':',
               switchpvs={'read': 'SQ:AMOR:PBY:PowerStatusRBV',
                          'write': 'SQ:AMOR:PBY:PowerStatus'},
               switchstates={'on': 1, 'off': 0},
               precision=0.1,
               timeout=None,
               window=5.0,
               ),
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
    dist_chopper_polarizer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of polarizer to chopper',
        distcomponent='dpolarizer',
        distreference='dchopper'
    ),
    dist_sample_polarizer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of polarizer to sample',
        distcomponent='dpolarizer',
        distreference='dsample'
    )
)
