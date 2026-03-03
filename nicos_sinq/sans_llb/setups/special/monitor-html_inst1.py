description = 'setup for the HTML status monitor'
group = 'special'

_sans1column = Row(
    Block(
        'Devices', [
            BlockRow(
                Field(name='attenuator',
                      dev='att', istext=False, width=15),
                Field(name='collimation distance',
                      dev='coll', istext=False, width=20),
                Field(name='main detector distance',
                      dev='detz', istext=False, width=20),
            ),
            BlockRow(
                Field(name='Wavelength',
                      dev='wavelength', istext = False, width=15),
            ),
            BlockRow(
                Field(name='Sample Changer',
                      dev='schanger', istext = False, width=15),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
        filename = '/home/status/instr1.html',
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