description = '1T electromagnet'

display_order = 53

includes = ['sample_magnet_table']

magprefix = 'SQ:AMOR:magnet:'

devices = dict(
    fma = device('nicos_sinq.devices.epics.sample_magnet.SampleMagnet',
                 description = 'fat sample magnet',
                 readpv = magprefix + 'fma:CurRBV',
                 writepv = magprefix + 'fma:CurSet',
                 wenable = magprefix + 'fma:STATUS',
                 renable = magprefix + 'fma:STATUS_RBV',
                 precision = .1,
                 pollinterval = 0.5,
                 abslimits = (-150., 150.),
                 visibility = ('metadata', 'namespace'),
                 ),
    se_B = device('nicos.devices.generic.magnet.CalibratedMagnet',
                  description = 'AMOR sample magnet',
                  currentsource = 'fma',
                  unit = 'T',
                  calibration = (-1/150, 0.0, 0.0, 0.0, 0.0)
                  ),
    )
