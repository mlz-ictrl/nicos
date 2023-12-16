description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=10),
            Field(name='Title', key='exp/title', width=50, istext=True),
            Field(name='Current status', key='exp/action', width=30, istext=True),
        ),
        BlockRow(
            Field(name='Sample', key='sample/samplename', width=40,
                 istext=True, maxlen=40),
            Field(name='Remark',   key='exp/remark',   width=40,
                 istext=True, maxlen=40),
        ),
        ],
    ),
)

_huberblock = SetupBlock('huber')

_servostarblock = SetupBlock('servostar')

_detectorblock = Block('Detector', [
    BlockRow(
        Field(name='Last Image', key='ikonl.lastfilename'),
    ),
    BlockRow(
        Field(dev='temp_ikonl'),
        Field(name='CCD status', key='ikonl/status[1]', width=15),
    ),
    BlockRow(
        Field(name='bin', key='ikonl.bin'),
        Field(name='flip (H,V)', key='ikonl.flip'),
        Field(name='rotation', key='ikonl.rotation'),
    ),
    BlockRow(
        Field(name='roi', key='ikonl.roi'),
        Field(name='hsspeed', key='ikonl.hsspeed', width=4),
        Field(name='vsspeed', key='ikonl.vsspeed', width=4),
        Field(name='pgain', key='ikonl.pgain', width=4),
    ),
    ],
    setups='detector_ikonl',
)

_shutterblock = SetupBlock('basic', 'shutters')

_basicblock = SetupBlock('basic', 'basic')

_sblblock = SetupBlock('sbl')

_lblblock = SetupBlock('lbl')

_detector_translationblock = SetupBlock('detector_translation')

_sockets1block = SetupBlock('sockets', 'cabinet1')

_sockets2block = SetupBlock('sockets', 'cabinet2')

_sockets3block = SetupBlock('sockets', 'cabinet3')

_sockets6block = SetupBlock('sockets', 'cabinet6')

_sockets7block = SetupBlock('sockets', 'cabinet7')

_filterwheelblock = SetupBlock('rm_filterwheel')

_selectorblock = SetupBlock('selector')

_monochromatorblock = SetupBlock('monochromator')

_ngiblock = SetupBlock('ngi')

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
    _monochromatorblock,
    _ngiblock,
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        description = 'Status Display',
        title = 'ANTARES Status Monitor',
        loglevel = 'info',
        cache = 'antareshw.antares.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Monospace',
        padding = 5,
        layout = [[_expcolumn], [_leftcolumn, _middlecolumn, _rightcolumn]],
    ),
)
