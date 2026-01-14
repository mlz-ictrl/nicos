description = 'Setup for virtual devices in simple mode'

display_order = 10

includes = ['base', 'diaphragm1', 'sample_stage', 'sample_alignment', 'detector_stage']
excludes = ['trough']

devices = dict(
    qz_defs = device('nicos_sinq.amor.devices.qz_defs.AmorQz',
                     description = 'AMOR parameter class',
                     div = 'div',
                     kappa = 'kappa',
                     kad = 'kad',
                     sample_tilt = 'sample_tilt',
                     mu = 'mu',
                     nu = 'nu',
                     det_nu = 'det_nu',
                     visibility = ('metadata', 'namespace'),
                     ),
    ql = device('nicos.devices.generic.ParamDevice',
                description = 'low limit of normal momentum transfer',
                device = 'qz_defs',
                parameter = 'ql',
                copy_status = True,
                fmtstr = '%6.3f',
                unit = '1/angstrom',
                ),
    qh = device('nicos.devices.generic.ParamDevice',
                description = 'high limit of normal momentum transfer',
                device = 'qz_defs',
                parameter = 'qh',
                copy_status = True,
                fmtstr = '%6.3f',
                unit = '1/angstrom',
                ),
    )