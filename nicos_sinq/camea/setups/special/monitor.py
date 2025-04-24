description = 'setup for the HTML status monitor'
group = 'special'

_cameacolumn = Row(
    Block(
        'Experiment', [
            BlockRow(
                Field(
                    name = 'Current status',
                    key= 'cameadet/status',
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
                    key = 'Sample/samplename',
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

_mono = Row(
    Block(
        'mono slit', [
            BlockRow(
                Field(name = 'msb (text)', dev = 'msb', width = 10),
            ),
            BlockRow(
                Field(name = 'mslit (height)', dev = 'mslit_height', width = 20),
            ),
        ]
    ),
)

_gonio = Row(
    Block(
        'gonio', [
            BlockRow(
                Field(name = 'gl', dev = 'gl', width = 20),
            ),
            BlockRow(
                Field(name = 'tl', dev = 'tl', width = 20),
            ),
        ]
    ),
)

_econf = Row(
    Block(
        'E config', [
            BlockRow(
                Field(name = 'ef', dev = 'ef', width = 20),
                Field(name = 'ei', dev = 'ei', width = 20),
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
                    picture = 'https://www.psi.ch/sites/default/files/styles/primer_full_xl/public/2024-06/screen_shot_2024-06-05_at_10.38.46.png.webp?itok=blHIPCHA',
                    width = 80,
                    height = 50,
                ),
	    ),
            BlockRow(
                Field(
                    name = 'Data (log)',
                    picture = './notebooks_QuickPlottingofData_5_0.png',
                    width = 72,
                    height = 44,
                ),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'Camea Status monitor',
        filename = '/afs/psi.ch/project/sinq/sinqstatus/camea/index.html',
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 16,
        layout = [
            [_cameacolumn],
            [_mono , _gonio],
	    [_econf ],
            [_live],
        ],
        noexpired = True,
    ),
)
