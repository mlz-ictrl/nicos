description = 'Control beam polarization'

group = 'lowlevel'

includes = ['collimation']

devices = dict(
    polarization = device('nicos_sinq.sans_llb.devices.polarization.PolarizationSwitcher',
        description = 'Changes polarization configuration on/off',
        unit = '',
        mapping = {
            'off': {
                '1250': ['ng', 'ng', 'ng', 'ng', 'ng', 'ng'],
                '3000': ['ng', 'ng', 'ng', 'ng', 'ng', 'ft'],
                '4250': ['ng', 'ng', 'ng', 'ng', 'ft', 'ft'],
                '8000': ['ng', 'ng', 'ng', 'ft', 'ft', 'ft'],
                '11750': ['ng', 'ng', 'ft', 'ft', 'ft', 'ft'],
                '15500': ['ng', 'ft', 'ft', 'ft', 'ft', 'ft'],
                '18500': ['ft', 'ft', 'ft', 'ft', 'ft', 'ft'],
            },
            'on': {
                '1250': ['pg', 'ng', 'ng', 'ng', 'ng', 'ng'],
                '3000': ['pg', 'ng', 'ng', 'ng', 'ng', 'ft'],
                '4250': ['pg', 'ng', 'ng', 'ng', 'ft', 'ft'],
                '8000': ['pg', 'ng', 'ng', 'ft', 'ft', 'ft'],
                '11750': ['pg', 'ng', 'ft', 'ft', 'ft', 'ft'],
                '15500': ['pg', 'ft', 'ft', 'ft', 'ft', 'ft'],
            },
        },
        fallback = '15500', # if collimation is 18500, move to 15500 when setting polarized mode
        coll='coll',
    ),
)
