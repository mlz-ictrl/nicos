description = 'Sample lift for 1T electromagnet'

display_order = 52

pvprefix = 'SQ:AMOR:mmac1:'
magprefix = 'SQ:AMOR:magnet:'

includes = ['smz_table']

devices = dict(
    fma = device('nicos_sinq.tasp.devices.slsmagnet.SLSMagnet',
        description = 'fat sample magnet',
        readpv = magprefix + 'fma:CurRBV',
        writepv = magprefix + 'fma:CurSet',
        wenable = magprefix + 'fma:STATUS',
        renable = magprefix + 'fma:STATUS_RBV',
        precision = .1,
        abslimits = (-100., 100.)
    ),
)
