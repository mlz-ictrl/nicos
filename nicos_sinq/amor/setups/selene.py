description = 'Selene support devices in AMOR'

pvprefix = 'SQ:AMOR:mota:'

includes = ['distances']

devices = dict(
    eoz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter z lift Selene support motor',
               motorpv=pvprefix + 'eoz',
               errormsgpv=pvprefix + 'eoz-MsgTxt',
               ),
    eom=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Counter omega Selene support motor',
               motorpv=pvprefix + 'eom',
               errormsgpv=pvprefix + 'eom-MsgTxt',
               ),
    dist_chopper_selene=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of selene to chopper',
        distcomponent='dselene',
        distreference='dchopper'
    ),
    dist_sample_selene=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of selene to sample',
        distcomponent='dselene',
        distreference='dsample'
    )
)
