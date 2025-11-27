description = 'setup for the HTML status monitor sample page'
group = 'special'

_monocolumn = Row(
    Block(
        'Sample table', [
            BlockRow(
                Field(name = 'mono (2theta)', dev = 'mtt', width = 20),
            ),
        ],
    ),   
)

_tempcolumn = Row(
    Block(
        'Temperature', [
            BlockRow(
                Field(name = 'temperature', dev = 'Ts', width = 20),
            ),
            BlockRow(
                Field(dev='Ts',       plot='temperature', plotwindow = 28800, width = 50, height = 30),
                Field(key='Ts/target', plot='temperature', plotwindow = 28800, width = 50, height = 30),
            ),
        ],
    ),   
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
        filename = '/home/status/sample.html', 
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Moni',
        fontsize = 12,
        padding = 3,
        layout = [
            [_monocolumn ],
	        [_tempcolumn],
        ],
        expectmaster = False,
        noexpired = True,
    ),
)
