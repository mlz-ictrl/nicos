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

_ngiblock = Block('Neutron Grating Interferometer', [
    BlockRow(
        Field(name='G0rz', dev='G0rz'),
        Field(name='G0ry', dev='G0ry'),
        # Field(name='G0tx', dev='G0tx'),
    ),
    BlockRow(
        Field(name='G1rz', dev='G1rz'),
        Field(name='G1tz', dev='G1tz'),
        # Field(name='G12rz', dev='G12rz'),
    ),
    ],
    setups='ngi*',
)

_leftcolumn = Column(
)

_middlecolumn = Column(
)

_rightcolumn = Column(
    _detectorblock,
    _ngiblock,
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        description = 'Status Display',
        title = 'ANTARES Status Monitor',
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Monospace',
        padding = 5,
        layout = [[_expcolumn], [_leftcolumn, _middlecolumn, _rightcolumn]],
    ),
)
