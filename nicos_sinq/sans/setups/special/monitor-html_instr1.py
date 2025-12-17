description = 'setup for the HTML status monitor'
group = 'special'


_nvscolumn = Row(
    Block(
        'Selector', [
            BlockRow(
                Field(name = 'wavelength', dev = 'vs_lambda', width = 20),
            ),
            BlockRow(
                Field(name = 'rot speed', dev = 'vs_speed', width = 20),
            ),
            BlockRow(
                Field(name = 'tilt', dev = 'vs_tilt', width = 20),
            ),
            BlockRow(
                Field(name = 'flow', dev = 'vs_flow', width = 20),
            ),
            BlockRow(
                Field(name = 'vacuum', dev = 'vs_vacuum', width = 20),
            ),
            BlockRow(
                Field(name = 'vibration', dev = 'vs_vibration', width = 20),
            ),
            BlockRow(
                Field(name = 'cbv', dev = 'vs_cbv', width = 20),
            ),
            BlockRow(
                Field(name = 'rotor T', dev = 'vs_rot_t', width = 20),
            ),
            BlockRow(
                Field(name = 'water (in)', dev = 'vs_water_tin', width = 20),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
	filename = '/home/sans/data/html/instr1.html',
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Moni',
        fontsize = 12,
        padding = 3,
        layout = [
            [_nvscolumn ],
        ],
	expectmaster=False,
        noexpired = True,
    ),
)
