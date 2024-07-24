description = 'Polarization analysis'

group = 'basic'

includes = [
    'pumabase', 'multianalyzer', 'multidetector', 'rdcad', 'analyzer',
    'monochromator', 'aliases', 'lengths', 'slits', 'opticalbench',
    'pollengths',
]

devices = dict(
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

startupcode = '''
med.opmode = 'pa'
'''
