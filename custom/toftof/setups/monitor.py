description = 'setup for the status monitor'
group = 'special'

_expcolumn = [
    ('Experiment', [
        [{'name': 'Proposal', 'key': 'exp/proposal', 'width': 7},
         {'name': 'Title', 'key': 'exp/title', 'width': 20,
          'istext': True, 'maxlen': 20},
         {'name': 'Sample', 'key': 'sample/samplename', 'width': 30,
          'istext': True},]]),
]

_reactorblock = ('Reactor', [
    [{'name': 'Power', 'dev': 'ReactorPower'}]
], 'reactor')

_chopperblock = ('Chopper system', [
    [{'name': 'Wavelength', 'dev': 'chWL'},
     {'name': 'Nom. Speed', 'dev': 'chSpeed'},
     {'name': 'Ratio', 'dev': 'chRatio'},
     {'name': 'CRC', 'dev': 'chCRC'},
     {'name': 'Slit type', 'dev': 'chST'}],
    [{'name': 'Disk 1', 'dev': 'chDS', 'item': 0},
     {'name': 'Disk 2', 'dev': 'chDS', 'item': 1},
     {'name': 'Disk 3', 'dev': 'chDS', 'item': 2},
     {'name': 'Disk 4', 'dev': 'chDS', 'item': 3},
     {'name': 'Disk 5', 'dev': 'chDS', 'item': 4},
     {'name': 'Disk 6', 'dev': 'chDS', 'item': 5},
     {'name': 'Disk 7', 'dev': 'chDS', 'item': 6}],
], 'chopper')

_vacuumblock = ('Vacuum', [
    [{'name': 'Gauge 1', 'dev': 'vac0'},
     {'name': 'Gauge 2', 'dev': 'vac1'},
     {'name': 'Gauge 3', 'dev': 'vac2'},
     {'name': 'Gauge 4', 'dev': 'vac3'},
     ]
], 'vacuum')

_tableblock = ('Sample table', [
    [{'dev': 'gx', 'dev': 'gy', 'dev': 'gz'}],
    [{'dev': 'gcx', 'dev': 'gcy', 'dev': 'gphi'}],
], 'table')

_slitblock = ('Sample slit', [
    [{'dev': 'slit', 'istext': True, 'width': 24}]
], 'slit')

_measblock = ('Measurement', [
    [{'key': 'm/timechannels', 'name': 'Time channels'},
     {'name': 'Last file', 'key': 'm/lastfilenumber'}],
    [{'key': 'm/laststats', 'item': 0, 'name': 'Time'},
     {'key': 'm/laststats', 'item': 1, 'name': 'Monitor'},
     {'key': 'm/laststats', 'item': 2, 'name': 'Counts'}],
    [{'key': 'm/laststats', 'item': 0, 'name': 'Monitor rate'},
     {'key': 'm/laststats', 'item': 0, 'name': 'Count rate'}],
], 'measurement')

_cryoblock = ('Cryo', [
    [{'key': 'cryo/setpoint', 'name': 'Setpoint'},
     {'dev': 'cryo_b', 'name': 'Sample'},
     {'dev': 'cryo_a', 'name': 'Sensor A'}],
    [{'key': 'cryo/p', 'name': 'P'}, {'key': 'cryo/i', 'name': 'I'},
     {'key': 'cryo/d', 'name': 'D'}, {'dev': 'cryo_p', 'name': 'pressure'}]
], 'cryo')

_otherblock = (
    'Other devices',
    [[{'dev': 'slit', 'width': 20, 'name': 'Slit'}],
     [{'dev': 'sw', 'width': 4, 'name': 'Switcher'}]],
    'misc')

_col1 = [
    _reactorblock,
    _chopperblock,
    _vacuumblock,
]

_col2 = [
    _tableblock,
    _slitblock,
]

_col3 = [
    _cryoblock,
#    _he3block,
#    _htfblock,
#    _stickblock,
]

_warnings = [
#    ('reactorpower/value', '< 20', 'Reactor off!'),
]

devices = dict(
    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     server = 'cpci1.toftof.frm2:14869',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 5,
                     layout = [[_expcolumn], [_col1, _col2, _col3]],
                     warnings = _warnings,
                     notifiers = [])
)
