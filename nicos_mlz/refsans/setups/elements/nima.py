description = 'Langmuir trough'

group = 'optional'

instrument_values = configdata('instrument.values')

tango_host = instrument_values['tango_base'] + 'test/nima_nima/io'
code_base = instrument_values['code_base'] + 'nima.'

devices = dict(
    nima_io = device('nicos.devices.tango.StringIO',
        tangodevice = tango_host,
        lowlevel = True,
    ),
    nima_area = device(code_base + 'MoveName',
        description = 'Area of Langmuir trough',
        comm = 'nima_io',
        fmtstr = '%.1f',
        abslimits = (60, 1100),
        speed = 600,
        unit = 'mm x mm',
    ),
    nima_speed = device(code_base + 'MoveName',
        description = 'todo',
        comm = 'nima_io',
        fmtstr = '%.1f',
        abslimits = (-600, 600),
        unit = 'mm/s',
    ),
    nima_pressure = device(code_base + 'MoveName',
        description = 'todo',
        comm = 'nima_io',
        abslimits = (0, 70),
        fmtstr = '%.1f',
        speed = 500,
        unit = '',
    ),
)
