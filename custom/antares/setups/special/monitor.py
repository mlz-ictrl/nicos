#  -*- coding: utf-8 -*-

name = 'setup for the status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=30),
            Field(name='Title', key='exp/title', width=10, istext=True),
            Field(name='Sample', key='sample/samplename', width=30,
                 istext=True, maxlen=30),
            Field(name='Current status', key='exp/action', width=15, istext=True),
            Field(name='Remark',   key='exp/remark',   width=15,
                 istext=True, maxlen=30),
            ),
        BlockRow(
            Field(name='Path', key='ccd/lastfilename', width=100),
        ),
        ],
    ),
)

_huberblock = Block('HUBER Small Sample Manipulator', [
    BlockRow(
        Field(dev='stx'), Field(dev='sty'), Field(dev='sry'),
        ),
    BlockRow(
        Field(dev='sgx'), Field(dev='sgz'),
        ),
    ],
    'huber',
)


_servostarblock = Block('Servostar Large Sample Manipulator', [
    BlockRow(
        Field(dev='stx'), Field(dev='sty'), Field(dev='sry'),
        ),
    ],
    'servostar',
)

_detectorblock = Block('Detector', [
    BlockRow(
        Field(name='Last Image', key='ccd.lastfilename'), Field(dev='ccdTemp'),
        ),
    BlockRow(
        Field(name='CCD status', key='ccd/status', width=25, item=1),
        ),
    BlockRow(
        Field(name='bin', key='ccd.bin'),
        Field(name='flip (H,V)', key='ccd.flip'),
        Field(name='rotation', key='ccd.rotation'),
        ),
    BlockRow(
        Field(name='roi', key='ccd.roi'),
        Field(name='hsspeed', key='ccd.hsspeed', width=4),
        Field(name='vsspeed', key='ccd.vsspeed', width=4),
        Field(name='pgain', key='ccd.pgain', width=4),
        ),
    ],
    'detector',
)

_shutterblock = Block('Shutters & Collimators', [
    BlockRow(
        Field(name='Reactor', dev='ReactorPower', format='%.1f', width=7),
        Field(dev='collimator', width=10),
        Field(dev='pinhole', width=10),
        ),
    BlockRow(
        Field(dev='shutter1', width=10, istext = True),
        Field(dev='shutter2', width=10, istext = True),
        Field(dev='fastshutter', width=10, istext = True),
        ),
    ],
    'basic',
)

_basicblock = Block('Info', [
    BlockRow(
        Field(name='Ambient', dev='center3_sens1'),
        Field(name='Flight Tube', dev='center3_sens2'),
        Field(dev='UBahn', width=12, istext=True),
        ),
    ],
    'basic',
)

_sblblock = Block('Small Beam Limiter', [
    BlockRow(
        Field(dev='sbl', name='sbl  [center[x,y], width[x,y]]', width=28),
        ),
    ],
    'sbl',
)

_lblblock = Block('Large Beam Limiter', [
    BlockRow(
        Field(dev='lbl', name='lbl  [center[x,y], width[x,y]]', width=28),
        ),
    ],
    'lbl',
)

_detector_translationblock = Block('Detector Translation', [
    BlockRow(
        Field(dev='dtx', width=13), Field(dev='dty', width=13),
        ),
    ],
    'detector_translation',
)

_sockets1block = Block('Sockets Cabinet 1', [
    BlockRow(
        Field(dev='socket01', width=9), Field(dev='socket02', width=9), Field(dev='socket03', width=9),
        ),
    ],
    'sockets',
)

_sockets2block = Block('Sockets Cabinet 2', [
    BlockRow(
        Field(dev='socket04', width=9), Field(dev='socket05', width=9), Field(dev='socket06', width=9),
        ),
    ],
    'sockets',
)

_sockets3block = Block('Sockets Cabinet 3', [
    BlockRow(
        Field(dev='socket07', width=9), Field(dev='socket08', width=9), Field(dev='socket09', width=9),
        ),
    ],
    'sockets',
)

_sockets6block = Block('Sockets Cabinet 6', [
    BlockRow(
        Field(dev='socket10', width=9), Field(dev='socket11', width=9), Field(dev='socket12', width=9),
        ),
    ],
    'sockets',
)

_sockets7block = Block('Sockets Cabinet 7', [
    BlockRow(
        Field(dev='socket13', width=9), Field(dev='socket14', width=9), Field(dev='socket15', width=9),
        ),
    ],
    'sockets',
)

_filterwheelblock = Block('Filterwheel', [
    BlockRow(
        Field(dev='filterwheel', width=14), Field(dev='pbfilter', width=14),
        ),
    ],
    'filterwheel',
)

_selectorblock = Block('Velocity Selector', [
    BlockRow(
        Field(name='Speed', dev='selector'), Field(name='Lambda',dev='selector_lambda'), Field(dev='selector_linear'),
        ),
    BlockRow(
        Field(dev='selector_vacuum', name='Vacuum'), Field(dev='selector_rtemp', name='Rotor Temp'),
        Field(dev='selector_vibrt', name='Vibration'),
        ),
    BlockRow(
        Field(dev='selector_winlt', name='Water Inlet'), Field(dev='selector_woutt', name='Water Outlet'),
        Field(name='Water Flow',dev='selector_wflow'),
        ),
    ],
    'selector',
)

_leftcolumn = Column(
    _shutterblock,
    _basicblock,
    _filterwheelblock,
    _sockets1block,
    _sockets2block,
    _sockets3block,
    _sockets6block,
    _sockets7block,
)

_middlecolumn = Column(
    _sblblock,
    _lblblock,
    _huberblock,
    _servostarblock,
    _detector_translationblock,
)

_rightcolumn = Column(
    _detectorblock,
    _selectorblock,
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                      description = 'Status Display',
                      title = 'ANTARES Status Monitor',
                      loglevel = 'info',
                      cache = 'antareshw.antares.frm2',
                      prefix = 'nicos/',
                      font = 'Luxi Sans',
                      valuefont = 'Monospace',
                      padding = 5,
                      layout = [[_expcolumn], [_leftcolumn, _middlecolumn, _rightcolumn]],
                    ),
)
