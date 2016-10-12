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
    Block('Monochromator', [
        BlockRow(Field(name='Crystal', dev='transm', istext=True)),
        BlockRow(Field(name='Wave length', dev='wav',)),
    ]
    ),
    Block('Sample table', [
        BlockRow(Field(dev='xt', format='%.1f')),
        BlockRow(Field(dev='yt')),
        BlockRow(Field(dev='zt', format='%.2f')),
        BlockRow(Field(dev='omgs')),
        BlockRow(Field(dev='tths')),
    ],
    setups = 'sampletable or vstressi',
    ),
    Block('Robot', [
        BlockRow(Field(dev='robx')),
        BlockRow(Field(dev='roby')),
        BlockRow(Field(dev='robz')),
        BlockRow(Field(dev='chir')),
        BlockRow(Field(dev='phir')),
        BlockRow(Field(dev='omgr')),
        BlockRow(Field(dev='tthr')),
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
        BlockRow(Field(dev='adet'),)
    ],
    ),
    Block('Gauge volume', [
        BlockRow(Field(dev='pst'),
                 Field(dev='psz'),
                 Field(dev='psw'),
                 Field(dev='psh'),),
        BlockRow(Field(dev='sst'),
                 Field(dev='ssw'),),
        BlockRow(Field(dev='mot1'),),
        BlockRow(Field(dev='rad_fhwm'),),
    ],
    ),
)

_eulerian = Column(
    Block('', [
        BlockRow(Field(dev='ReactorPower',)),
        BlockRow(Field(dev='hv1',),
                 Field(dev='hv2',)),
    ],
    ),
    Block('Eulerian', [
        BlockRow(Field(dev='chis')),
        BlockRow(Field(dev='phis')),
    ],
    setups = 'eulerian*',
    ),
    Block('Tesile machine', [
        BlockRow(Field(dev='teload',)),
        BlockRow(Field(dev='tepos',)),
        BlockRow(Field(dev='teext',)),
    ],
    setups = 'tensile',
    ),
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'stressictrl.stressi.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [Row(_expcolumn),
                               Row(_sampletable, _measurement, _eulerian)],
                    ),
)
