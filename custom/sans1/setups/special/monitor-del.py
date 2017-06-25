description = 'setup for the status monitor for SANS1'
group = 'special'


_interfaceboxtop = Block('Interface Box (top)', [
        BlockRow(Field(name='Humidity',    dev='tub_h1'),
                 Field(name='Temperature', dev='tub_t6'),
        ),
    ],
#
# Only used if a master has this setup loaded, if missed it will be used
# unconditionally
#
#   setups='tube_environment',
)

_interfaceboxbottom = Block('Interface Box (bottom)', [
        BlockRow(Field(name='Humidity', dev='tub_h2'),
                 Field(name='Temperature', dev='tub_t7'),
        ),
    ],
    # setups='tube_environment',
)

_nim_voltage = Block('Voltage Detector NIM', [
        BlockRow(Field(name='+', dev='tub_v1'),
                 Field(name='-', dev='tub_v2'),
        ),
    ],
    # setups='tube_environment',
)

_electronicsbox = Block('Temperature Electronics Box', [
         BlockRow(Field(name='left', dev='tub_t1'),
                  Field(name='middle', dev='tub_t2'),
                  Field(name='right', dev='tub_t3'),
         )
    ],
    # setups='tube_environment',
)

_warnings = [
    ('tub_t1/value', '> 35', 'Temp in electronics box > 35'),
    ('tub_t2/value', '> 35', 'Temp in electronics box > 35'),
    ('tub_t3/value', '> 35', 'Temp in electronics box > 35'),
    ('tub_v1/value', '< 5.75', 'NIM voltage (+) < 5.75'),
    ('tub_v2/value', '> -5.75', 'NIM voltage (-) > -5.75'),
]

_rightcolumn = [
    _nim_voltage,
    _electronicsbox,
]

_leftcolumn = [
    _interfaceboxtop,
    _interfaceboxbottom,
]

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'SANS1 Detector electronics monitor',
                     loglevel = 'info',
                     cache = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 16,
                     padding = 5,
                     layout = [
#                                 [_expcolumn],
                                  [_leftcolumn, _rightcolumn]
                              ],
                    ),
)
