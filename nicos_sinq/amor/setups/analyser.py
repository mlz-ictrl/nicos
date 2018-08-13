description = 'Analyser devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

includes = ['distances']

devices = dict(
    aom=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Analyser tilt motor',
               motorpv=pvprefix + 'aom',
               errormsgpv=pvprefix + 'aom-MsgTxt',
               ),
    aoz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Analyser z position of rotation axis motor',
               motorpv=pvprefix + 'aoz',
               errormsgpv=pvprefix + 'aoz-MsgTxt',
               ),
    atz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Analyser z position relative to rotation axis motor',
               motorpv=pvprefix + 'atz',
               errormsgpv=pvprefix + 'atz-MsgTxt',
               ),
    aby=device('nicos_sinq.amor.devices.epics_amor_magnet.EpicsAmorMagnet',
               epicstimeout=3.0,
               description='Analyzer magnet',
               basepv='SQ:AMOR:ABY',
               pvdelim=':',
               switchpvs={'read': 'SQ:AMOR:ABY:PowerStatusRBV',
                          'write': 'SQ:AMOR:ABY:PowerStatus'},
               switchstates={'on': 1, 'off': 0},
               precision=0.1,
               timeout=None,
               window=5.0,
               ),
    dist_chopper_analyzer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of analyzer to chopper',
        distcomponent='danalyzer',
        distreference='dchopper'
    ),
    dist_sample_analyzer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of analyzer to sample',
        distcomponent='danalyzer',
        distreference='dsample'
    )
)
