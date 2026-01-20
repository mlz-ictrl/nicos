description = 'setup for the HTML status monitor'
group = 'special'

_sans1column = Row(
    Block(
        'SANS-1 Status', [
            BlockRow(
                Field(
                    name = 'Title',
                    key = 'exp/title',
                    istext = True,
                    width = 40
                )
            ),
            BlockRow(
                Field(name = 'Last run no.', key = 'exp/lastscan'),
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
                Field(name='Current status',
                      key='exp/action',
                      width=15,
                      istext=True),
                Field(name='timer',
                      dev='elapsedtime', width=15),
            ),
            BlockRow(
                Field(name='shutter',
                      dev='shutter', istext = True, width=30),
            ),
            BlockRow(
                Field(name='proton beam',
                      dev='protoncount', width=30),
            ),
            BlockRow(
                Field(name='sansdet',
                      key='sansdet/status',item=1, width=30),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
        filename = '/home/sans/data/html/status.html',
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Moni',
        fontsize = 12,
        padding = 3,
        layout = [
            [_sans1column],
        ],
        expectmaster=False,
        noexpired = True,
    ),
)
