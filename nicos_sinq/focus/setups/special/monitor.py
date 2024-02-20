description = 'setup for the HTML status monitor'
group = 'special'

_focuscolumn = Column(
    Block(
        'Experiment',
        [
            BlockRow(
                Field(
                    name = 'Current status',
                    key = 'exp/action',
                    width = 30,
                    istext = True,
                    maxlen = 30
                ),
            ),
            BlockRow(
                Field(name = 'Last file', key = 'exp/lastpoint'),
            ),
            BlockRow(
                Field(
                    name = 'Current Sample',
                    key = 'sample/samplename',
                    width = 40,
                    istext = True
                ),
            ),
            BlockRow(
                Field(
                    name = 'Title',
                    key = 'exp/title',
                    istext = True,
                    width = 60
                )
            ),
            # BlockRow(Field(name = 'Temperature', dev = 'Ts', width = 20)),
        ],
    ),
)

_choppercolumn = Column(
    Block(
        'Chopper', [
            BlockRow(
                Field(name = 'Fermi speed', dev = 'ch1_speed', width = 20),
            ),
            BlockRow(
                Field(name = 'Disk speed', dev = 'ch2_speed', width = 20),
            ),
            BlockRow(
                Field(name = 'Chopper phase', dev = 'ch_phase', width = 20),
            ),
        ]
    ),
)

_live = Column(
    Block(
        'Live image of Detector',
        [
            BlockRow(
                Field(
                    name = 'Data (lin)',
                    picture = 'sans1-online/live_lin.png',
                    width = 64,
                    height = 64
                ),
                Field(
                    name = 'Data (log)',
                    picture = 'sans1-online/live_log.png',
                    width = 64,
                    height = 64
                ),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'FOCUS Status monitor',
        filename = '/afs/psi.ch/project/sinq/sinqstatus/focus.html',
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [
            Row(_focuscolumn),
            Row(_choppercolumn),
        ],
        noexpired = True,
    ),
)
