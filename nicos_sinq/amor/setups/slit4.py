description = 'Slit 4 devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motc:'

includes = ['slit1']

devices = dict(
    d4t=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 4 opening motor',
               motorpv=pvprefix + 'd4t',
               errormsgpv=pvprefix + 'd4t-MsgTxt',
               lowlevel=True
               ),
    d4b=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 4 z position (lower edge) motor',
               motorpv=pvprefix + 'd4b',
               errormsgpv=pvprefix + 'd4b-MsgTxt',
               lowlevel=True
               ),
    slit4=device('nicos.devices.generic.slit.Slit',
                 description='Slit 4 with left, right, bottom and top motors',
                 opmode='4blades',
                 left='d1l',
                 right='d1r',
                 top='d4t',
                 bottom='d4b',
                 ),
    slit4_opening=device('nicos_sinq.amor.devices.slit.SlitOpening',
                         description='Slit 4 opening controller',
                         slit='slit4'
                         ),
    dist_chopper_slit4=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of slit 4 to chopper',
        distcomponent='dslit4',
        distreference='dchopper'
    ),
    dist_sample_slit4=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of slit 4 to sample',
        distcomponent='dslit4',
        distreference='dsample'
    )
)
