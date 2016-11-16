#  -*- coding: utf-8 -*-
description = 'Configuration for raspi01 status monitor'

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
    setups='huber',
)


_servostarblock = Block('Servostar Large Sample Manipulator', [
    BlockRow(
        Field(dev='stx_servostar'), Field(dev='sty_servostar'), Field(dev='sry_servostar'),
        ),
    ],
    setups='servostar',
)

_detectorikonlcolumn = Column(
    Block('Detector Andor IkonL', [
    BlockRow(
        Field(name='Path', key='Exp/proposalpath', width=40, format='%s/'),
        Field(name='Last Image', key='exp/lastpoint', width=60),
        ),
    BlockRow(
        Field(name='Status', key='ikonl/status[1]', width=25),
        Field(dev='ikonlTemp'),
        Field(name='hsspeed', key='ikonl.hsspeed', width=4),
        Field(name='vsspeed', key='ikonl.vsspeed', width=4),
        Field(name='pgain', key='ikonl.pgain', width=4),
        ),
    BlockRow(
        Field(name='roi', key='ikonl.roi'),
        Field(name='bin', key='ikonl.bin'),
        Field(name='flip (H,V)', key='ikonl.flip'),
        Field(name='rotation', key='ikonl.rotation'),
        ),
    ],
    setups='detector_ikonl',
    ),
)

_detectorneocolumn = Column(
    Block('Detector Andor Neo', [
    BlockRow(
        Field(name='Path', key='Exp/proposalpath', width=40, format='%s/'),
        Field(name='Last Image', key='exp/lastpoint', width=60),
        ),
    BlockRow(
        Field(name='Status', key='neo/status[1]', width=25),
        Field(dev='neoTemp'),
        Field(name='elshuttermode', key='neo.elshuttermode', width=6),
        Field(name='readoutrate MHz', key='neo.readoutrate', width=4),
        ),
    BlockRow(
        Field(name='roi', key='neo.roi'),
        Field(name='bin', key='neo.bin'),
        Field(name='flip (H,V)', key='neo.flip'),
        Field(name='rotation', key='neo.rotation'),
        ),
    ],
    setups='detector_neo',
    ),
)

_shutterblock = Block('Shutters & Collimators', [
    BlockRow(
        Field(name='Reactor', dev='ReactorPower', width=7),
        Field(dev='collimator', width=10),
        Field(dev='pinhole', width=10),
        ),
    BlockRow(
        Field(dev='shutter1', width=10, istext = True),
        Field(dev='shutter2', width=10, istext = True),
        Field(dev='fastshutter', width=10, istext = True),
        ),
    ],
    setups='basic',
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
    setups='basic',
)

_sblblock = Block('Small Beam Limiter', [
    BlockRow(
        Field(dev='sbl', name='sbl  [center[x,y], width[x,y]]', width=28),
        ),
    ],
    setups='sbl',
)

_lblblock = Block('Large Beam Limiter', [
    BlockRow(
        Field(dev='lbl', name='lbl  [center[x,y], width[x,y]]', width=28),
        ),
    ],
    setups='lbl',
)

_detector_translationblock = Block('Detector Translation', [
    BlockRow(
        Field(dev='dtx', width=13), Field(dev='dty', width=13),
        ),
    ],
    setups='detector_translation',
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
                      padding = 1,
                      layout = [[_expcolumn], [_detectorikonlcolumn], [_detectorneocolumn], [_leftcolumn, _rightcolumn]],
                    ),
)
