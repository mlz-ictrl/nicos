description = 'PUMA triple-axis setup with FRM2-Detector'

group = 'basic'

sysconfig = dict(
    datasinks = ['nxtassink'],
)

includes = [
    'pumabase',
    'seccoll',
    'collimation',
    'ios',
    # 'seccoll',
    'collimation',
    # 'ios',
    # 'hv',
    # 'notifiers',
    'detector',
]
