description = 'Frame overlap devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

includes = ['distances']

devices = dict(
    fom=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Frame overlap tilt motor',
               motorpv=pvprefix + 'fom',
               errormsgpv=pvprefix + 'fom-MsgTxt',
               ),
    ftz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Frame overlap z position of rotation axis motor',
               motorpv=pvprefix + 'ftz',
               errormsgpv=pvprefix + 'ftz-MsgTxt',
               ),
    dist_chopper_filter=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of filter to chopper',
        distcomponent='dfilter',
        distreference='dchopper'
    ),
    dist_sample_filter=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of filter to sample',
        distcomponent='dfilter',
        distreference='dsample'
    )
)
