description = 'setup for the HTML status monitor'
group = 'special'

_collcolumn = Row(
    Block(
        'Collimator', [
            BlockRow(
                Field(name = 'collimation', dev = 'coll', width = 20),
            ),
            BlockRow(
                Field(name = 'collimation (target)', key = 'coll/target', width = 20),
            ),
            BlockRow(
                Field(name = 'polarisator', dev = 'pol', istext = True, width = 20),
            ),
            BlockRow(
                Field(name = 'polarisator (target)', key = 'pol/target', istext = True, width = 20),
            ),
        ],
    ),
)

_flipcolumn = Row(
    Block(
        'Flipper', [
            BlockRow(
                Field(name = 'flipper (state)', dev = 'flip_state', width = 20),
            ),
            BlockRow(
                Field(name = 'flipper (amplitude)', dev = 'flip_amp', width = 20),
            ),
            BlockRow(
                Field(name = 'flipper (frequency)', dev = 'flip_freq', width = 20),
            ),
        ],
    ),
)

_attcolumn = Row(
    Block(
        'Attenuator', [
            BlockRow(
                Field(name = 'att', dev = 'att', istext = True, width = 20),
            ),
            BlockRow(
                Field(name = 'attpos', dev = 'attpos', width = 20),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
        filename = '/home/sans/data/html/instr2.html',
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Moni',
        fontsize = 12,
        padding = 3,
        layout = [
            [_collcolumn, _attcolumn ],
            [_flipcolumn],
        ],
	expectmaster=False,
        noexpired = True,
    ),
)
