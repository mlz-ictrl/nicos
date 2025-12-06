description = 'setup for the HTML status monitor status page'
group = 'special'

_focus = Row(
    Block(
        'FOCUS Status', [
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
                Field(name='Current status', 
                      key='exp/action', 
                      width=15,
                      istext=True),
                Field(name='timer', 
                      dev='elapsedtime', width=15),
            ),
            BlockRow(
                Field(name='FC', 
                      dev='ch1_speed', width=15),
                Field(name='DC', 
                      dev='ch2_speed', width=15),
            ),
            BlockRow(
                Field(name='proton beam', 
                      dev='protoncount', width=30),
            ),
            BlockRow(
                Field(name='focusdet', 
                      key='focusdet/status',item=1, width=30),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
        filename = '/home/status/status.html', 
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Moni',
        fontsize = 12,
        padding = 3,
        layout = [
            [_focus],
        ],
        expectmaster=False,
        noexpired = True,
    ),
)
