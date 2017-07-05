# This setup file configures the nicos status monitor.

description = 'setup for the LAUE html status monitor'
group = 'special'

_expcolumn = Column(
    Block(
        'Experiment',
        [
            BlockRow(
                Field(name = 'Proposal', key = 'exp/proposal', width = 7),
                Field(
                    name = 'Title',
                    key = 'exp/title',
                    width = 15,
                    istext = True,
                    maxlen = 15
                ),
                Field(
                    name = 'Sample',
                    key = 'sample/samplename',
                    width = 15,
                    istext = True,
                    maxlen = 15
                ),
            ),
            BlockRow(
                Field(
                    name = 'Remark',
                    key = 'exp/remark',
                    width = 30,
                    istext = True,
                    maxlen = 30
                ),
                Field(
                    name = 'Current status',
                    key = 'exp/action',
                    width = 30,
                    istext = True
                ), Field(name = 'Last file', key = 'exp/lastimage')
            ),
        ],
    ),
)

col1 = Column(
    Block(
        'Detector',
        [
            BlockRow(
                Field(
                    name = 'Status',
                    key = 'det1/status',
                    width = 15,
                    istext = True,
                    maxlen = 15
                ),
            ),
            BlockRow(
                Field(name = 'Distance', dev = 'detz', format = '%.1f'),
                Field(name = '2-theta', dev = 'twotheta', format = '%.1f'),
            ),
        ],
    ),
)

col2 = Column(
    Block(
        'Kappa',
        [
            BlockRow(
                Field(dev = 'phi', format = '%.2f'),
                Field(dev = 'omega', format = '%.2f'),
                Field(dev = 'kappa', format = '%.2f'),
            ),
            BlockRow(
                Field(dev = 'stx', format = '%.2f'),
                Field(dev = 'sty', format = '%.2f'),
                Field(dev = 'stz', format = '%.2f'),
            ),
        ],
    ),
)

# for cc setup
lauecryo = Block(
    'Cryostat',
    [
        BlockRow(
            Field(dev = 't_laue', name = 'Regulation'),
            Field(dev = 't_laue_a', name = 'Sensor A'),
            Field(dev = 't_laue_b', name = 'Sensor B'),
        ),
        BlockRow(
            Field(key = 't_laue/setpoint', name = 'Setpoint'),
            Field(key = 't_laue/p', name = 'P', width = 5),
            Field(key = 't_laue/i', name = 'I', width = 5),
            Field(key = 't_laue/d', name = 'D', width = 5),
        ),
    ],
    setups = 'ccrlaue',
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'LAUE Status monitor',
        filename = '/data/lauestatus/index.html',
        interval = 10,
        loglevel = 'info',
        cache = 'lauectrl.laue.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [
            [_expcolumn],
            [
                col1,
                col2,
            ],
            [BlockRow(lauecryo)],
        ]
    ),
)
