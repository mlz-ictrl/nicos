
sysconfig = dict(
    experiment = 'Exp',
)

packs = ['0a', '0b', '1']
cbox_components = [
    'fg_freq', 'reg_amp','coil1_c1', 'coil1_c2', 'coil1_c1c2serial',
    'coil1_c3', 'coil1_transformer', 'coil2_c1', 'coil2_c2', 'coil2_c1c2serial',
    'coil2_c3', 'coil2_transformer', 'diplexer', 'power_divider'
]

devices = dict(
    Sample = device('nicos_virt_mlz.reseda.devices.sample.Sample',
    ),
    Exp = device('nicos_mlz.reseda.devices.Experiment',
        dataroot = 'nicos_mlz/reseda/test/data',
        sample = 'Sample',
    ),
    selector_speed = device('nicos.devices.generic.VirtualMotor',
        abslimits = (0, 28500),
        precision = 10,
        unit = 'rpm',
    ),
    selcradle = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-10, 10),
        precision = 0.001,
        unit = 'deg',
    ),
    selector_lambda = device('nicos_mlz.reseda.devices.SelectorLambda',
        seldev = 'selector_speed',
        tiltdev = 'selcradle',
        unit = 'A',
        fmtstr = '%.2f',
        twistangle = 48.27,
        length = 0.25,
        beamcenter = 0.115,
        maxspeed = 28500,
    ),
    selector_delta_lambda = device('nicos_mlz.reseda.devices.SelectorLambdaSpread',
        lamdev = 'selector_lambda',
        unit = '%',
        fmtstr = '%.1f',
        n_lamellae = 64,
        d_lamellae = 0.8,
        diameter = 0.32,
    ),

    arm1_rot = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-95, 5),
        fmtstr = '%.3f',
        unit = 'deg',
        curvalue = -55,
    ),
    arm2_rot = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-15, 58),
        fmtstr = '%.3f',
        unit = 'deg',
        curvalue = 0,
    ),
    armctrl = device('nicos_mlz.reseda.devices.ArmController',
        arm1 = 'arm1_rot',
        arm2 = 'arm2_rot',
        minangle = 50,
    ),
    psd_channel = device('nicos_virt_mlz.reseda.devices.CascadeDetector',
        description = 'CASCADE detector channel',
        foilsorder = [5, 4, 3, 0, 1, 2, 6, 7],
    ),
    sf_0a = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        abslimits = (0, 5),
        # precision = 0.01,
        unit = 'A',
    ),
    sf_0b = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        abslimits = (0, 5),
        # precision = 0.01,
        unit = 'A',
    ),
    sf_1 = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        abslimits = (0, 5),
        # precision = 0.01,
        unit = 'A',
    ),
    hsf_0a = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        abslimits = (0, 5),
        # precision = 0.01,
        unit = 'A',
    ),
    hsf_0b = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        abslimits = (0, 5),
        # precision = 0.01,
        unit = 'A',
    ),
    hsf_1 = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        abslimits = (0, 5),
        # precision = 0.01,
        unit = 'A',
    ),
    hrf_0a = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 100),
        # precision = 0.02,
    ),
    hrf_0b = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 100),
        # precision = 0.02,
    ),
    hrf_1a = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 100),
        # precision = 0.02,
    ),
    hrf_1b = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 100),
        # precision = 0.02,
    ),
    nse0 = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.5f',
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        abslimits = (-5, 5),
        # precision = 0.0005,
    ),
    nse1 = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.5f',
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        abslimits = (-5, 5),
        # precision = 0.0005,
    ),
    phase = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        abslimits = (0, 5),
        # precision = 0.005,
    ),
    echotime = device('nicos_mlz.reseda.devices.EchoTime',
        description = 'Echo time and tunewave table device',
        wavelength = 'selector_lambda',
        dependencies = ['gf%i' % i for i in ([1, 2] + list(range(4, 11)))]
        + ['hsf_%s' % entry for entry in packs]
        + ['sf_%s' % entry for entry in packs]
        + ['hrf_0a','hrf_0b', 'hrf_1a', 'hrf_1b']
        + ['nse0', 'nse1']
        + ['cbox_%s_%s' % (pack, component)
            for pack in ['0a', '0b', '1a']
            for component in cbox_components],
        unit = 'ns',
        fmtstr = '%g'
    ),
)

for sname in ['cbox_0a', 'cbox_0b', 'cbox_1a']:
    devices['%s_fg_freq' % sname] = device('nicos.devices.generic.ManualMove',
        pollinterval = 30,
        fmtstr = '%.4g',
        unit = 'Hz',
        abslimits = (30000, 5000000),
        default = 35000,
    )
    devices['%s_reg_amp' % sname] = device('nicos.devices.generic.ManualMove',
        unit = 'V',
        abslimits = (0, 10),
    )
    devices['%s_fg_amp' % sname] = device('nicos.devices.generic.ManualMove',
        pollinterval = 5,
        unit = 'V',
        abslimits = (0, 10),
        default = 0,
    )
    devices['%s' % sname] = device('nicos_mlz.reseda.devices.CBoxResonanceFrequency',
        pollinterval = 30,
        unit = 'Hz',
        power_divider = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1],
            unit = '',
            fmtstr = '%d',
        ),
        highpass = device('nicos.devices.generic.ManualSwitch',
            states = list(range(128)),
            unit = '',
            fmtstr = '%d',
        ),
        fg = '%s_fg_freq' % setupname,
        diplexer = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1],
            unit = '',
            fmtstr = '%d',
        ),
        coil1_c1 = device('nicos.devices.generic.ManualSwitch',
            states = list(range(64)),
            unit = '',
            fmtstr = '%d',
        ),
        coil1_c2 = device('nicos.devices.generic.ManualSwitch',
            states = list(range(32)),
            unit = '',
            fmtstr = '%d',
        ),
        coil1_c3 = device('nicos.devices.generic.ManualSwitch',
            states = list(range(16)),
            unit = '',
            fmtstr = '%d',
        ),
        coil1_c1c2serial = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1],
            unit = '',
            fmtstr = '%d',
        ),
        coil1_transformer = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1, 2],
            unit = '',
            fmtstr = '%d',
        ),
        coil2_c1 = device('nicos.devices.generic.ManualSwitch',
            states = list(range(64)),
            unit = '',
            fmtstr = '%d',
        ),
        coil2_c2 = device('nicos.devices.generic.ManualSwitch',
            states = list(range(32)),
            unit = '',
            fmtstr = '%d',
        ),
        coil2_c3 = device('nicos.devices.generic.ManualSwitch',
            states = list(range(16)),
            unit = '',
            fmtstr = '%d',
        ),
        coil2_c1c2serial = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1],
            unit = '',
            fmtstr = '%d',
        ),
        coil2_transformer = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1, 2],
            unit = '',
            fmtstr = '%d',
        ),
    )

for i in range(0, 11):
    devices[f'gf{i}'] = device('nicos.devices.generic.ManualMove',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 119, # maxage should not be a multiple of pollinterval!
        unit = 'A',
        abslimits = (0, 5),
        # precision = 0.005,
    )
