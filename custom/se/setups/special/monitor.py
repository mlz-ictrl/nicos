description = 'setup for the status monitor'
group = 'special'

Row = Column = BlockRow = lambda *args: args
Block = lambda *args, **kwds: (args, kwds)
Field = lambda *args, **kwds: args or kwds

_expcolumn = [
    ('Experiment', [
        [{'name': 'Proposal', 'key': 'exp/proposal', 'width': 7},
         {'name': 'Title', 'key': 'exp/title', 'width': 30,
          'istext': True, 'maxlen': 40},
         {'name': 'Sample', 'key': 'sample/samplename', 'width': 30,
          'istext': True},
         {'name': 'Remark', 'key': 'exp/remark', 'width': 30,
          'istext': True}],
        ],
    ),
]

_reactorblock = ('Reactor', [
    [{'name': 'Power', 'dev': 'ReactorPower'}]
    ],
)

_chopperblock = ('Chopper system', [
    [{'name': 'Wavelength', 'dev': 'chWL', 'format': '%.1f'},
     {'name': 'Nom. Speed', 'dev': 'chSpeed', 'format': '%.0f'},
     {'name': 'Act. Speed', 'dev': 'ch', 'format': '%.0f'}],
    [{'name': 'Ratio', 'dev': 'chRatio'},
     {'name': 'CRC', 'dev': 'chCRC'},
     {'name': 'Slit type', 'dev': 'chST'}],
    '---',
    [{'name': 'Disk 1', 'dev': 'chDS', 'item': 0, 'format': '%.1f'},
     {'name': 'Disk 2', 'dev': 'chDS', 'item': 1, 'format': '%.1f'},
     {'name': 'Disk 3', 'dev': 'chDS', 'item': 2, 'format': '%.1f'},
     {'name': 'Disk 4', 'dev': 'chDS', 'item': 3, 'format': '%.1f'}],
    [{'name': 'Disk 5', 'dev': 'chDS', 'item': 4, 'format': '%.1f'},
     {'name': 'Disk 6', 'dev': 'chDS', 'item': 5, 'format': '%.1f'},
     {'name': 'Disk 7', 'dev': 'chDS', 'item': 6, 'format': '%.1f'}],
    ],
)

_vacuumblock = ('Vacuum', [
    [{'name': 'Gauge 1', 'dev': 'vac0', 'format': '%.2g'},
     {'name': 'Gauge 2', 'dev': 'vac1', 'format': '%.2g'},
     {'name': 'Gauge 3', 'dev': 'vac2', 'format': '%.2g'},
     {'name': 'Gauge 4', 'dev': 'vac3', 'format': '%.2g'},
     ]
    ],
)

_tableblock = ('Sample table', [
    [{'dev': 'gx'}, {'dev': 'gy'}, {'dev': 'gz'}],
    [{'dev': 'gcx'}, {'dev': 'gcy'}, {'dev': 'gphi'}],
    ],
)

_slitblock = ('Sample slit', [
    [{'dev': 'slit', 'istext': True, 'width': 24, 'name': 'Slit'}]
    ],
)

_measblock = ('Measurement', [
    [{'key': 'm/timechannels', 'name': 'Time channels'},
     {'name': 'Last file', 'key': 'm/lastfilename'}],
    [{'key': 'm/laststats', 'item': 0, 'name': 'Time', 'format': '%.1f'},
     {'key': 'm/laststats', 'item': 1, 'name': 'Monitor', 'format': '%d'},
     {'key': 'm/laststats', 'item': 2, 'name': 'Counts', 'format': '%d'}],
    [{'key': 'm/laststats', 'item': 0, 'name': 'Monitor rate', 'format': '%.1f'},
     {'key': 'm/laststats', 'item': 0, 'name': 'Count rate', 'format': '%.1f'}],
    ],
)

_cryoblock = ('Cryo', [
    [{'key': 'cryo/setpoint', 'name': 'Setpoint'},
     {'dev': 'cryo_b', 'name': 'Sample'},
     {'dev': 'cryo_a', 'name': 'Sensor A'}],
    [{'key': 'cryo/p', 'name': 'P'}, {'key': 'cryo/i', 'name': 'I'},
     {'key': 'cryo/d', 'name': 'D'}, {'dev': 'cryo_p', 'name': 'pressure'}]
    ],
)

_col1 = [
    _reactorblock,
    _chopperblock,
    _vacuumblock,
]

_col2 = [
    _tableblock,
    _slitblock,
    _measblock,
]

_col3 = [
    _cryoblock,
#    _he3block,
#    _htfblock,
#    _stickblock,
]

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'localhost:14869',
                     prefix = 'nicos/',
                     font = 'Ubuntu',
                     valuefont = 'DejaVu Sans Mono',
                     padding = 5,
                     layout = [[_expcolumn], [_col1, _col2, _col3]],
                    ),
)
