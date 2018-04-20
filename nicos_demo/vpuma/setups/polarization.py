description = 'Polarization analysis'

group = 'basic'

includes = ['multianalyzer', 'multidetector', 'cad', 'analyzer', 'monochromator']

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
    rd6_cad = device('nicos.devices.generic.Axis',
        description = "Combined axis of 'rd6' and 'cad'",
        motor = 'rd6',
        precision = 0.001,
    ),
    # rd6_cad = device('nicos_mlz.puma.devices.comb_ax.CombAxis',
    #     description = 'Sample scattering angle Two Theta',
    #     motor = 'st_phi',
    #     # coder = 'co_phi',
    #     # obs = [],
    #     precision = 0.005,
    #     offset = 0.21,
    #     maxtries = 5,
    #     loopdelay = 1,
    #     fix_ax = 'psi_puma',
    #     iscomb = False,
    # ),
)
