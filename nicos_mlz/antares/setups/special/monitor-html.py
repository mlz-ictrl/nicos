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
        Field(dev='T', name='CCI 3He'),
        ),
    BlockRow(
        Field(plot='Temperature', name='CCI 3He', dev='T_cci3he2', width=60, height=40, plotwindow=3600),
        ),
    ],
    setups='ccr7',
)

_tensileblock = Block('Tensile Rig', [
    BlockRow(
	Field(dev='teext', name='Extension'),
	Field(dev='tepos', name='Position'),
	Field(dev='teload', name='load'),
	),
    BlockRow(
	Field(plot='Extension', dev='teext', width=60, height=40, plotwindow=3600),
        ),
    BlockRow(
	Field(plot='Position', dev='tepos', width=60, height=40, plotwindow=3600),
        ),
    BlockRow(
	Field(plot='Load', dev='teload', width=60, height=40, plotwindow=3600),
        ),
    ],
    setups='tensile',
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
        Field(dev='sr830[0]', name='X (V)', format='%1.6f', width=12),
        Field(dev='sr830[1]', name='Y (V)', format='%1.6f', width=12)#
        ),
    BlockRow(
        Field(dev='sr830[2]', name='abs (V)', format='%1.6f', width=12),
        Field(dev='sr830[3]', name='phase (deg)', width=12)
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

_ngi_jcnsblock = Block('Neutron Grating Interferometer', [
    BlockRow(
        Field(name='G0rz', dev='G0rz'), Field(name='G0ry', dev='G0ry'), Field(name='G0tx', dev='G0tx'),
        ),
    BlockRow(
        Field(name='G1rz', dev='G1rz'), Field(name='G1tz', dev='G1tz'), Field(name='G12rz', dev='G12rz'),
        ),
    ],
    setups='ngi_jcns',
)

_cryomanipulatorblock = Block('Cryostat Manipulator', [
    BlockRow(
        Field(name='ctx', dev='ctx'), Field(name='cty', dev='cty'), Field(name='cry', dev='cry'),
        ),
    ],
    setups='cryomanipulator',
)

# generic Cryo-stuff
cryos = []
cryosupps = []
cryoplots = []
cryodict = dict(cci3he1='3He-insert', cci3he2='3He-insert', cci3he3='3He-insert',
                cci3he4he1='Dilution-insert', cci3he4he2='Dilution-insert')
for cryo, name in cryodict.items():
    cryos.append(
        Block('%s %s' % (name, cryo.title()), [
            BlockRow(
                Field(dev='t_%s'   % cryo, name='Regulation', max=38),
                Field(dev='t_%s_a' % cryo, name='Sensor A', max=38),
                Field(dev='t_%s_b' % cryo, name='Sensor B',max=7),
            ),
            BlockRow(
                Field(key='t_%s/setpoint' % cryo, name='Setpoint'),
                Field(key='t_%s/p' % cryo, name='P', width=7),
                Field(key='t_%s/i' % cryo, name='I', width=7),
                Field(key='t_%s/d' % cryo, name='D', width=7),
            ),
            ],
            setups=cryo,
        )
    )
    cryosupps.append(
        Block('%s-misc' % cryo.title(),[
            BlockRow(
                Field(dev='%s_p1' % cryo, name='Pump', width=10),
                Field(dev='%s_p4' % cryo, name='Cond.', width=10),
            ),
            BlockRow(
                Field(dev='%s_p5' % cryo, name='Dump', width=10),
                Field(dev='%s_p6' % cryo, name='IVC', width=10),
            ),
            BlockRow(
                Field(key='%s_flow' % cryo, name='Flow', width=10),
            ),
            ],
            setups=cryo,
        )
    )
    cryoplots.append(
        Block(cryo.title(), [
            BlockRow(
                Field(widget='nicos.guisupport.plots.TrendPlot',
                      plotwindow=3600, width=25, height=25,
                      devices=['t_%s/setpoint' % cryo, 't_%s' % cryo],
                      names=['Setpoint', 'Regulation'],
                ),
            ),
            ],
            setups=cryo,
        )
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

_leftcolumn += Column(*cryos) + Column(*cryosupps) + Column(*cryoplots)

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
    _ngi_jcnsblock,
    _tensileblock
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
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
