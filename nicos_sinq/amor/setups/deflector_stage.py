description = 'Lift and pitch of deflector and flight tube'

display_order = 40

includes = [
    'base', 'diaphragm2', 'sample_stage', 'detector_stage'
    ]

pvprefix = 'SQ:AMOR:masterMacs1:'

devices = dict(
    ltz = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
                 description = 'Lift (z translation) of deflector & flight tube',
                 motorpv = pvprefix + 'ltz',
                 unit = 'mm',
                 visibility = ('devlist', 'metadata', 'namespace'),
                ),
    lom = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
                 description = 'Tilt (pitch) of deflector & flight tube',
                 motorpv = pvprefix + 'lom',
                 unit = 'deg',
                 visibility = ('devlist', 'metadata', 'namespace'),
                ),
    kap = device('nicos_sinq.amor.devices.deflector_defs.AmorDeflector',
                 description = 'Beam inclination and deflector devices',
                 distances = 'distances',
                 kad = 'kad',
                 lom = 'lom',
                 ltz = 'ltz',
                 d2z = 'd2z',
                 f_zoffset = 'f_zoffset',
                 s_zoffset = 's_zoffset',
                 soz = 'soz',
                 nu = 'nu',
                 ka0 = 'ka0',
                 det_zoffset = 'det_zoffset',
                 visibility = ('metadata', 'namespace'),
                 unit = 'deg',
                ),
    )

alias_config = {
    'kappa': {'kap': 100},
}
