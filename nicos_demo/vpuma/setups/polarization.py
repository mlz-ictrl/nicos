description = 'Polarization analysis'

group = 'basic'

includes = ['multianalyzer', 'multidetector', 'cad', 'analyzer',
            'monochromator', 'aliases']

devices = dict(
    polana = device('nicos.devices.tas.Monochromator',
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
    rd6_cad = device('nicos_mlz.puma.devices.StackedAxis',
        description = "Combined axis of 'rd6' and 'cad'",
        # description = 'Sample scattering angle Two Theta',
        bottom = 'cad',
        top = 'rd6',
    ),
)

alias_config = {
    'ana': {'polana': 200},
}
