description = 'setup for the HTML status monitor'
group = 'special'

_st1column = Row(
    Block(
        'Sample table', [
            BlockRow(
                Field(name = 'a3 (rotation)', dev = 'a3', width = 20),
            ),
            BlockRow(
                Field(name = 'sg (goniometer)', dev = 'sg', width = 20),
            ),
            BlockRow(
                Field(name = 'spos (sample changer)', dev = 'spos', width = 20),
            ),
        ],
    ),
)

_st2column = Row(
    Block(
        'Sample table', [
            BlockRow(
                Field(name = 'z (vertical)', dev = 'z', width = 20),
            ),
            BlockRow(
                Field(name = 'xu (hor. perp to n)', dev = 'xu', width = 20),
            ),
            BlockRow(
                Field(name = 'xo (hor. perp. to n)', dev = 'xo', width = 20),
            ),
            BlockRow(
                Field(name = 'yo (hor. parall. to n)', dev = 'yo', width = 20),
            ),
        ],
    ),
)


_tempcolumn = Row(
    Block(
        'Temperature', [
            BlockRow(
                Field(name = 'temperature', dev = 'T', width = 20),
            ),
            BlockRow(
                Field(dev='T',        plot='temperature', plotwindow = 28800, width = 50, height = 30),
                Field(dev='Ts',       plot='temperature', plotwindow = 28800, width = 50, height = 30),
                Field(key='T/target', plot='temperature', plotwindow = 28800, width = 50, height = 30),
            ),
        ],
    ),
)

_Bfieldcolumn = Row(
    Block(
        'magnetic field', [
            BlockRow(
                Field(name = 'B(Tesla)', dev = 'B', width = 20),
            ),
            BlockRow(
                Field(dev='B',        plot='B(Tesla)', plotwindow = 28800, width = 50, height = 30),
                Field(key='B/target', plot='B(Tesla)', plotwindow = 28800, width = 50, height = 30),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
        filename = '/home/sans/data/html/sample.html',
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Moni',
        fontsize = 12,
        padding = 3,
        layout = [
            [_st1column, _st2column ],
            [_tempcolumn],
            [_Bfieldcolumn],
        ],
	expectmaster=False,
        noexpired = True,
    ),
)
