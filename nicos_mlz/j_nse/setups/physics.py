description = 'High level physics JNSE devices'
group = 'optional'

modules = ['nicos_mlz.j_nse.commands.jnse']

includes = [
    'counter',
    'ccmotors',
    'motors',
    'power',
    'selector',
    'spsanalog',
    'thermojet',
]

devices = {
    'HEAD': device(
        'nicos_mlz.j_nse.devices.NestHead',
        description = 'Root of the instrument configuration tree',
        instrument = 'NSE',
        visibility = ('metadata', 'namespace'),
        controlled = ['moana',
                      'mo_cc11a', 'mo_cc11b', 'mo_cc12a', 'mo_cc12b',
                      'mo_cc21a', 'mo_cc21b', 'mo_cc22a', 'mo_cc22b',
                      'mo_cc31a', 'mo_cc31b', 'mo_cc32a', 'mo_cc32b',],
        nextnodes = ['Lambda',],
    ),
    'Lambda': device(
        'nicos_mlz.j_nse.devices.NestTransform',
        description = 'Neutron wavelength selector',
        unit = 'Å',
        fmtstr = '%.1f',
        controlled = ['dlambda', 'phase_deg_perA1', 'phase_deg_perA2',],
        nextnodes = ['Q',],
        dev = 'selector_speed',
        informula = '124096.72 / x + 0.00440399 * x ** 0.5266 - 0.529403',
        outformula = '16000.0 * 8.0 / x * (0.96151 + 4.877865 / x ** 2.43012)',
    ),
    'Q': device(
        'nicos_mlz.j_nse.devices.NestMapped',
        description = 'Momentum transfer selector',
        unit = 'Å⁻¹',
        fmtstr = '%.2f',
        precision = 0.005,
        controlled = ['mophi', 'mogamma', 'mobeta', 'mopsi',],
        nextnodes = ['t_nom',],
    ),
    't_nom': device(
        'nicos_mlz.j_nse.devices.NestMapped',
        description = 'Nominal Fourier time selector',
        unit = 'ns',
        fmtstr = '%.2f',
        controlled = [f'pow{i:02d}' for i in range(1, 39)
                      if i not in [14, 15, 31]] + ['dum1', 'dum2', 'dum3',
                                                   't_act', 'countscale', 'J',],
    ),
}

# some virtual devices to store NIST table parameters
# are to be seen only in metainfo scope
devs = ['dlambda', 'phase_deg_perA1', 'phase_deg_perA2', 't_act', 'countscale', 'J',]
for dev in devs:
    devices[f'{dev}'] = device(
        'nicos_mlz.j_nse.devices.Basic',
        visibility = ('metadata', ),
        description = f'{dev}',
        unit = '',
    )

# j-nse virtual coils to be seen only in metainfo scope
for i in range(1, 4):
    devices[f'dum{i}'] = device(
        'nicos_mlz.j_nse.devices.Basic',
        visibility = ('metadata', ),
        description = f'Virtual coil dum{i}',
        unit = 'A',
    )


def topic(cmd):
    return f'{cmd}_\n\n.. _{cmd}: cmd:{cmd}\n\n'

help_topics = {'J-nse commands': topic('nsescan')}
