description = 'rd/cad combined devices'

group = 'lowlevel'

includes = ['cad', 'multidet', 'multiana']

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
    ana_polarization = device('nicos.devices.tas.Monochromator',
        description = 'analyzer wavevector',
        unit = 'A-1',
        dvalue = 3.355,
        theta = 'ra6',
        twotheta = 'rd6_cad',
        focush = None,
        focusv = None,
        abslimits = (0.1, 10),
        scatteringsense = -1,
        crystalside = -1,
    ),
)

alias_config = {
    'ana': {'ana_polarization': 200},
}
