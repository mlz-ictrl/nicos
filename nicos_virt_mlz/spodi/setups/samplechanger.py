description = 'Sample changer and rotation'

group = 'optional'

devices = dict(
    samr = device('nicos.devices.generic.ManualSwitch',
        description = '(de-)activates the sample rotation',
        states = ('off', 'on'),
    ),
    sams_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Motor position of the sample change selection wheel',
        abslimits = (-10, 370),
        speed = 5,
        unit = 'deg',
        visibility = (),
    ),
    sams_a = device('nicos.devices.generic.Axis',
        description = 'Position of sample selection wheel',
        motor = 'sams_m',
        precision = 0.05,
        visibility = (),
    ),
    sams = device('nicos_mlz.spodi.devices.SampleChanger',
        description = 'Sample Changer drum',
        moveables = ['sams_a'],
        mapping = {
            'S1': [-3.04],
            'S2': [33.11],
            'S3': [68.8],
            'S4': [104.95],
            'S5': [140.93],
            'S6': [177.20],
            'S7': [212.91],
            'S8': [249.07],
            'S9': [285.11],
            'S10': [321.03],
        },
        fallback = '?',
        fmtstr = '%s',
        precision = [0.1],
        blockingmove = True,
        unit = '',
    ),
)
display_order = 60

alias_config = {
}
