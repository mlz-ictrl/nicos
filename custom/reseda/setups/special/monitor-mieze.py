description = 'RESEDA status monitor MIEZE'
group = 'special'

_expcolumn = Column(
    Block(
        'Experiment',
        [
            BlockRow(
                Field(name = 'Exp no.', key = 'info/number', width = 7),
                Field(
                    name = 'Exp title',
                    key = 'info/titel',
                    width = 20,
                    istext = True
                ),
                Field(name = 'User', key = 'info/user', istext = True),
                Field(
                    name = 'Sample',
                    key = 'info/sample',
                    width = 10,
                    istext = True
                ),
                Field(name = 'Test-Length', dev = 'length', width = 10),
                Field(name = 'LSD', key = 'info/lsd', istext = True),
            ),
        ],
    ),
)

_motorblock = Block(
    'Arm Motors',
    [
        BlockRow(
            Field(name = 'TwoTheta 1', dev = 'm1', unit = 'Deg'),
            Field(name = 'TwoTheta 2', dev = 'm2', unit = 'Deg'),
        ),
    ],
    setups = 'motors',
)

_sampletableblock = Block(
    'Sample Table',
    [
        BlockRow(
            Field(name = 'Ty - M3', dev = 'm3', unit = 'mm'),
            Field(name = 'Tx - M4', dev = 'm4', unit = 'mm'),
        ),
        BlockRow(
            Field(name = 'gl - M5', dev = 'm5', unit = 'Deg'),
            Field(name = 'gu - M6', dev = 'm6', unit = 'Deg'),
            Field(name = 'Omega', dev = 'm7', unit = 'Deg'),
        ),
    ],
    setups = 'motors',
)

_frequenciesblock = Block(
    'Frequencies',
    [
        BlockRow(
            Field(
                name = 'Coil 2 - F0',
                dev = 'F0',
                unit = 'Hz',
                width = 8,
                format = "%.0f"
            ),
            Field(
                name = 'Coil 1 - F1',
                dev = 'F1',
                unit = 'Hz',
                width = 8,
                format = "%.0f"
            ),
            Field(
                name = 'Detector',
                dev = 'F2',
                unit = 'Hz',
                width = 8,
                format = "%.0f"
            ),
        ),
        BlockRow(
            Field(name = 'Coil 2 - RF0', dev = 'RF0', unit = 'V', width = 8),
            Field(name = 'Coil 1 - RF1', dev = 'RF1', unit = 'V', width = 8),
            Field(name = 'Detector', dev = 'RF2', unit = 'V', width = 8),
        ),
        BlockRow(
            Field(name = 'Coil 2 - Fu0', dev = 'Fu0', unit = 'A', width = 8),
            Field(name = 'Coil 1 - Fu1', dev = 'Fu1', unit = 'A', width = 8),
            Field(name = 'Detector - Fu2', dev = 'Fu2', unit = 'A', width = 8),
        ),
    ],
    setups = 'frequencies',
)

_tempblock = Block(
    'Temperature',
    [
        BlockRow(
            Field(key = 't/setpoint', name = 'Setpoint'),
            Field(name = 'TA', dev = 'TA', unit = 'K'),
            Field(name = 'TB', dev = 'TB', unit = 'K'),
            Field(name = 'TC', dev = 'TC', unit = 'K'),
            Field(name = 'TD', dev = 'TD', unit = 'K'),
        ),
        BlockRow(
            Field(dev = 'TA', plot = 'TA', interval = 300, width = 50),
            # Field(key='t/setpoint', name='SetP', plot='TA', interval=300),
        ),
        BlockRow(
            Field(dev = 'TD', plot = 'TD', interval = 300, width = 50),
        )
    ],
    setups = 'temperature',
)

_currentblock = Block(
    'Current',
    [
        BlockRow(
            Field(name = 'B0', dev = 'B01', unit = 'A', width = 10),
            Field(name = 'B0', dev = 'B02', unit = 'V', width = 10),
            Field(name = 'B2', dev = 'B21', unit = 'A', width = 10),
            Field(name = 'B2', dev = 'B22', unit = 'V', width = 10),
        ),
    ],
    setups = 'powersupply',
)

_powersupplyblock = Block(
    'Power Supply',
    [
        BlockRow(
            Field(name = 'B6', dev = 'B52_c', unit = 'A', width = 10),
            Field(name = 'B6', dev = 'B52_v', unit = 'V', width = 10),
            Field(name = 'B7', dev = 'B53_c', unit = 'A', width = 10),
            Field(name = 'B7', dev = 'B53_v', unit = 'V', width = 10),
        ),
    ],
    setups = 'powersupply',
)

_scatteringblock = Block(
    'Scattering',
    [
        BlockRow(
            Field(
                name = 'Sel',
                dev = 'Sel',
                unit = 'rpm',
                width = 10,
                format = "%.0f"
            ),
            Field(name = 'Lambda', dev = 'Lambda', width = 10, unit = 'A'),
            Field(name = 'Q1', dev = 'Q1', width = 10, unit = '1/A'),
            Field(name = 'Q2', dev = 'Q2', width = 10, unit = '1/A'),
            Field(name = 'MIEZE time', dev = 'TauM', width = 10, unit = 'ns')
        ),
    ],
    setups = 'frequencies',
)

_capacitanceblock = Block(
    'Capacitance',
    [
        BlockRow(
            Field(name = 'C0', dev = 'C1', unit = '', width = 10),
            Field(name = 'C2', dev = 'C2', unit = '', width = 10),  ##  K/h 0
            Field(name = 'C1', dev = 'C3', unit = '', width = 10),
            Field(name = 'C4', dev = 'C4', unit = '', width = 10),  ##  K/h 1
            Field(name = 'C2', dev = 'C5', unit = '', width = 10),
            Field(name = 'C6', dev = 'C6', unit = '', width = 10),  ##  K/h 2
        ),
    ],
    setups = 'capacitance',
)

_attenuatorsblock = Block(
    'Attenuators',
    [
        BlockRow(
            Field(name = 'Att0', dev = 'Att0', unit = ''),
            Field(name = 'Att1', dev = 'Att1', unit = ''),
            Field(name = 'Att2', dev = 'Att2', unit = ''),
        ),
    ],
    setups = 'atts_slits',
)

_rightcolumn = Column(
    _scatteringblock,
    _motorblock,
    _sampletableblock,
    _currentblock,
    _powersupplyblock,
)

_leftcolumn = Column(
    _tempblock,
    _frequenciesblock,
    _attenuatorsblock,
    _capacitanceblock,
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'RESEDA MIEZE',
        loglevel = 'info',
        cache = 'resedahw2.reseda.frm2',
        font = 'Luxi Sans',
        fontsize = 18,
        valuefont = 'Consolas',
        padding = 5,
        layout = [Row(_expcolumn), Row(_rightcolumn, _leftcolumn)],
    )
)
