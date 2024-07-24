description = 'rd/cad combined devices'

group = 'lowlevel'

includes = ['cad']

devices = dict(
    rd5_cad = device('nicos_mlz.puma.devices.StackedAxis',
        description = "Combined axis of 'rd5' and 'cad'",
        bottom = 'cad',
        top = 'rd5',
    ),
    rd6_cad = device('nicos_mlz.puma.devices.StackedAxis',
        description = "Combined axis of 'rd6' and 'cad'",
        bottom = 'cad',
        top = 'rd6',
    ),
    rd7_cad = device('nicos_mlz.puma.devices.StackedAxis',
        description = "Combined axis of 'rd7' and 'cad'",
        bottom = 'cad',
        top = 'rd7',
    ),
)
