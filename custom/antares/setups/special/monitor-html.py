#  -*- coding: utf-8 -*-

description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Sample', key='sample/samplename', width=50,
                 istext=True, maxlen=50),
            Field(name='Remark',   key='exp/remark',   width=50,
                 istext=True, maxlen=50),
            Field(name='Current status', key='exp/action', width=30, istext=True),
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
        Field(name='Last Image', key='ikonl.lastfilename', width=60),
        ),
    BlockRow(
        Field(name='Status', key='ikonl/status', width=25, item=1),
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
        Field(name='Last Image', key='neo.lastfilename', width=60),
        ),
    BlockRow(
        Field(name='Status', key='neo/status', width=25, item=1),
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
        Field(name='He bottle',dev='He_pressure'),
        ),
    BlockRow(Field(plot='Pressure', name='Ambient', dev='center3_sens1', width=60, height=40, plotwindow=24*3600),
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

_sockets1block = Block('Sockets Cabinet 1', [
    BlockRow(
        Field(dev='socket01', width=9), Field(dev='socket02', width=9), Field(dev='socket03', width=9),
        ),
    ],
    setups='sockets',
)

_sockets2block = Block('Sockets Cabinet 2', [
    BlockRow(
        Field(dev='socket04', width=9), Field(dev='socket05', width=9), Field(dev='socket06', width=9),
        ),
    ],
    setups='sockets',
)

_sockets3block = Block('Sockets Cabinet 3', [
    BlockRow(
        Field(dev='socket07', width=9), Field(dev='socket08', width=9), Field(dev='socket09', width=9),
        ),
    ],
    setups='sockets',
)

_sockets6block = Block('Sockets Cabinet 6', [
    BlockRow(
        Field(dev='socket10', width=9), Field(dev='socket11', width=9), Field(dev='socket12', width=9),
        ),
    ],
    setups='sockets',
)

_sockets7block = Block('Sockets Cabinet 7', [
    BlockRow(
        Field(dev='socket13', width=9), Field(dev='socket14', width=9), Field(dev='socket15', width=9),
        ),
    ],
    setups='sockets',
)

_filterwheelblock = Block('Filterwheel', [
    BlockRow(
        Field(dev='filterwheel', width=14), Field(dev='pbfilter', width=14),
        ),
    ],
    setups='filterwheel',
)

_selectorblock = Block('Velocity Selector', [
    BlockRow(
        Field(name='Speed', dev='selector'),
        Field(name='Lambda',dev='selector_lambda'),
        Field(name='Tilt', dev='selector_tilt'),
        Field(name='Position', dev='selector_inout'),
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
    setups='selector',
)

_temperatureblock = Block('Cryo Temperature', [
    BlockRow(
	Field(dev='T', name='Sensor A'),
	Field(dev='T_susi', name='T_susi'),
	),
    BlockRow(
	Field(plot='Temperature', name='Sensor A', dev='T_cc_A', width=60, height=40, plotwindow=3600),
	Field(plot='Temperature', name='T_susi', dev='T_susi'),
        ),
    ],
    setups='cc_puma',
)

_garfieldblock = Block('Garfield Magnet', [
        BlockRow(Field(dev='B_amagnet', name='B'), Field(dev='amagnet_connection', name='Mode') ),
    ],
    setups='amagnet',
)

_flipperblock = Block('Mezei-Flip', [
        BlockRow('dct1', 'dct2', Field(dev='flip', width=5)),
    ],
    setups='mezeiflip',
)

_lockinblock = Block('Lock-In', [
    BlockRow(
        Field(dev='sr830', name='X (V)', item=0, format='%1.6f', width=12),
        Field(dev='sr830', name='Y (V)', item=1, format='%1.6f', width=12)#
        ),
    BlockRow(
        Field(dev='sr830', name='abs (V)', item=2, format='%1.6f', width=12),
        Field(dev='sr830', name='phase (deg)', item=3, width=12)
        ),
    BlockRow(
	Field(plot='Lock-In', name='X', dev='sr830[0]', width=40, height=20, plotwindow=1*3600),
	Field(plot='Lock-In', name='Y', dev='sr830[1]'),
	),
    ],
    setups='sr830',
)

_monochromatorblock = Block('Double Crystal PG Monochromator', [
    BlockRow(
        Field(name='Lambda', dev='mono'), Field(name='Position', dev='mono_inout')
        ),
    BlockRow(
        Field(dev='mr1'), Field(dev='mr2'), Field(dev='mtz'),
        ),
    ],
    setups='monochromator',
)

_ngiblock = Block('Neutron Grating Interferometer', [
    BlockRow(
        Field(name='G0rz', dev='G0rz'), Field(name='G0ry', dev='G0ry'), Field(name='G0tx', dev='G0tx'),
        ),
    BlockRow(
        Field(name='G1rz', dev='G1rz'), Field(name='G1tz', dev='G1tz'), Field(name='G12rz', dev='G12rz'),
        ),
    ],
    setups='ngi',
)

_cryomanipulatorblock = Block('Cryostat Manipulator', [
    BlockRow(
        Field(name='ctx', dev='ctx'), Field(name='cty', dev='cty'), Field(name='cry', dev='cry'),
        ),
    ],
    setups='cryomanipulator',
)


_leftcolumn = Column(
    _shutterblock,
    _basicblock,
    _temperatureblock,
    _selectorblock,
    _filterwheelblock,
    _sockets1block,
    _sockets2block,
    _sockets3block,
)

_rightcolumn = Column(
    _sblblock,
    _lblblock,
    _huberblock,
    _servostarblock,
    _detector_translationblock,
    _cryomanipulatorblock,
    _monochromatorblock,
    _flipperblock,
    _lockinblock,
    _garfieldblock,
    _sockets6block,
    _sockets7block,
    _ngiblock,
)


devices = dict(
    Monitor = device('services.monitor.html.Monitor',
                      description = 'Status Display',
                      title = 'ANTARES Status Monitor',
                      filename = '/antarescontrol/status.html',
                      loglevel = 'info',
                      interval = 10,
                      cache = 'antareshw.antares.frm2',
                      prefix = 'nicos/',
                      font = 'Luxi Sans',
                      valuefont = 'Monospace',
                      fontsize = 15,
                      padding = 5,
                      layout = [[_expcolumn], [_detectorikonlcolumn], [_detectorneocolumn],[_leftcolumn, _rightcolumn]],
                    ),
)
