# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Last file', key='exp/lastscan')),
        BlockRow(Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40)),
    ],
    )
)

_sampletable = Column(
    Block('Sample table', [
        BlockRow(Field(dev='xt', format='%.1f')),
        BlockRow(Field(dev='yt')),
        BlockRow(Field(dev='zt', format='%.2f')),
        BlockRow(Field(dev='omgs')),
        BlockRow(Field(dev='tths')),
    ],
    setups = 'sampletable or vstressi',
    ),
    Block('Eulerian', [
        BlockRow(Field(dev='chis')),
        BlockRow(Field(dev='phis')),
    ],
    setups = 'eulerian*',
    ),
    Block('Robot', [
        BlockRow(Field(dev='xt')),
        BlockRow(Field(dev='yt')),
        BlockRow(Field(dev='zt')),
        BlockRow(Field(dev='chis')),
        BlockRow(Field(dev='phis')),
        BlockRow(Field(dev='omgs')),
        BlockRow(Field(dev='tths')),
        BlockRow(Field(dev='robt')),
        BlockRow(Field(dev='robs')),
        BlockRow(Field(dev='robsl')),
        BlockRow(Field(dev='robsj')),
        BlockRow(Field(dev='robsr')),
    ],
    setups = 'robot*',
    ),
)

_measurement = Column(
    Block('Measurement', [
        BlockRow(Field(name='timer', key='tim1/value'),
                 Field(name='monitor', key='mon/value'),
                 Field(name='counts', key='image/value'),)
    ],
    ),
    Block('Primary slit', [
        BlockRow(Field(dev='pst'),
                 Field(dev='psz'),
                 Field(dev='psw'),
                 Field(dev='psh'),),
    ],
    setups = 'primaryslit*',
    ),
    Block('Secondary optics', [
        BlockRow(Field(dev='sst'),
                 Field(dev='ssw'),),
    ],
    setups = 'secondaryslit',
    ),
    Block('Radial collimator', [
        BlockRow(Field(dev='mot1'),
                 Field(dev='rad_fwhm'),),
    ],
    setups = 'radial',
    ),
    Block('Tensile machine', [
        BlockRow(Field(dev='teload',)),
        BlockRow(Field(dev='tepos',)),
        BlockRow(Field(dev='teext',)),
    ],
    setups = 'tensile*',
    ),
)

_eulerian = Column(
    Block('', [
        BlockRow(Field(dev='ReactorPower',)),
        BlockRow(Field(dev='hv1',),
                 Field(dev='hv2',)),
    ],
    ),
    Block('Monochromator', [
        BlockRow(Field(name='Crystal', dev='transm', istext=True)),
        BlockRow(Field(name='Wave length', dev='wav',)),
    ]
    ),
    Block('Sample Temperature', [
         BlockRow(Field(dev='T')),
    ],
    setups = 'stressihtf or htf* or ccr*',
    ),
)

_image = Column(
    Block('', [
        BlockRow(
            Field(name='Data (linear)', picture='stressi-online/live_lin.png',
                  refresh=1, width=24, height=24),
            Field(name='Data (log)', picture='stressi-online/live_log.png',
                  refresh=1, width=24, height=24),
        ),
    ]
    )
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'STRESS-SPEC status monitor',
        loglevel = 'info',
        interval = 10,
        # Use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the hostname (official
        # computer name) or an IP address.
        filename = '/stressicontrol/status.html',
        cache = 'stressictrl.stressi.frm2',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        prefix = 'nicos/',
        # padding = 2,
        fontsize = 24,
        layout = [Row(_expcolumn),
                  Row(_sampletable, _measurement, _eulerian),
                  Row(_image)],
    ),
)
