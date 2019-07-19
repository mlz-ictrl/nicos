description = 'sample changer sword'

group = 'plugplay'

includes = ['sample_changer']

devices = dict(
    ccmsanssc_switch = device('nicos.devices.generic.ManualSwitch',
        description = 'position switch for pressure valve',
        lowlevel = False,
        states = ('free', 'closed'),
    ),
    ccmsanssc_motor = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = (0, 600),
        unit = 'mm',
    ),
    ccmsanssc_axis = device('nicos_mlz.sans1.devices.ccmsanssc.SwordAxis',
        description = 'translation of the sword',
        abslimits = (0, 600),
        motor = 'ccmsanssc_motor',
        startdelay = 1,
        stopdelay = 1,
        switch = 'ccmsanssc_switch',
        switchvalues = (2, 1),
        fmtstr = '%.2f',
        precision = 0.2,
        dragerror = 5,
    ),
    ccmsanssc_position = device('nicos.devices.generic.MultiSwitcher',
        description = 'position of the sample changer sword',
        moveables = ['ccmsanssc_axis'],
        mapping = {
            1: [4],
            2: [69],
            3: [134],
            4: [199],
            5: [264],
            6: [329],
            7: [394],
            8: [459],
            9: [524],
            10: [589]
        },
        precision = [0.2],
        fallback = 0,
        fmtstr = '%d',
    ),
)

alias_config = {'SampleChanger': {'ccmsanssc_position': 100},}
