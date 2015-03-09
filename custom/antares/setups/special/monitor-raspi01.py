#  -*- coding: utf-8 -*-

name = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=10),
            Field(name='Title', key='exp/title', width=60, istext=True),
            Field(name='Current status', key='exp/action', width=30, istext=True),
        ),
        BlockRow(
            Field(name='Sample', key='sample/samplename', width=50,
                 istext=True, maxlen=50),
            Field(name='Remark',   key='exp/remark',   width=50,
                 istext=True, maxlen=50),
        ),
        ],
    ),
)

_huberblock = Block('HUBER Small Sample Manipulator', [
    BlockRow(
        Field(dev='stx_huber'), Field(dev='sty_huber'), Field(dev='sry_huber'),
        ),
    BlockRow(
        Field(dev='sgx_huber'), Field(dev='sgz_huber'),
        ),
    ],
    'huber',
)


_servostarblock = Block('Servostar Large Sample Manipulator', [
    BlockRow(
        Field(dev='stx_servostar'), Field(dev='sty_servostar'), Field(dev='sry_servostar'),
        ),
    ],
    'servostar',
)

_detectorcolumn = Column(
    Block('Detector', [
    BlockRow(
        Field(name='Path', key='Exp/proposalpath', width=40, format='%s/'),
        Field(name='Last Image', key='ccd.lastfilename', width=60),
        ),
    BlockRow(
        Field(name='CCD status', key='ccd/status', width=25, item=1),
        Field(dev='ccdTemp'),
        Field(name='hsspeed', key='ccd.hsspeed', width=4),
        Field(name='vsspeed', key='ccd.vsspeed', width=4),
        Field(name='pgain', key='ccd.pgain', width=4),
        ),
    BlockRow(
        Field(name='roi', key='ccd.roi'),
        Field(name='bin', key='ccd.bin'),
        Field(name='flip (H,V)', key='ccd.flip'),
        Field(name='rotation', key='ccd.rotation'),
        ),
    ],
    'detector',
    ),
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
    BlockRow(Field(plot='Pressure', name='Ambient', dev='center3_sens1', width=40, height=20, plotwindow=24*3600),
        Field(plot='Pressure', name='Flight Tube', dev='center3_sens2')),
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


_leftcolumn = Column(
    _shutterblock,
    _basicblock,
)

_rightcolumn = Column(
    _sblblock,
    _lblblock,
    _huberblock,
    _servostarblock,
    _detector_translationblock,
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
                      layout = [[_expcolumn], [_detectorcolumn], [_leftcolumn, _rightcolumn]],
                    ),
)
