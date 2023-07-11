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

_huberblock = SetupBlock('huber')

_servostarblock = SetupBlock('servostar')

_rscblock = Block('Rotation Sample Stick', [
    BlockRow(
        Field(dev='sth_rsc03'),
    ),
    ],
    setups='rsc03',
)

_detectorikonlcolumn = Column(
    Block('Detector Andor IkonL', [
        BlockRow(
            Field(name='Last Image', key='exp/lastpoint', width=60),
        ),
        BlockRow(
            Field(name='Status', key='ikonl/status[1]', width=25),
            Field(name='Temp', dev='temp_ikonl'),
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
            Field(dev='temp_neo'),
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

_detectorzwo01column = Column(
    Block('Detector ZWO 01', [
        BlockRow(
            Field(name='Last Image', key='exp/lastpoint', width=60),
        ),
        BlockRow(
            Field(name='Status', key='zwo01/status[1]', width=25),
            Field(dev='temp_zwo01'),
        ),
        BlockRow(
            Field(name='roi', key='zwo01.roi'),
            Field(name='bin', key='zwo01.bin'),
            Field(name='flip (H,V)', key='zwo01.flip'),
            Field(name='rotation', key='zwo01.rotation'),
        ),
        ],
        setups='detector_zwo01',
    ),
)

_live = Column(
    Block('Live image of Detector', [
        BlockRow(
            Field(picture='antares-online/live_lin.png',
                  width=96, height=96),
        ),
        ],
        setups='liveimage_public'
    ),
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

_temperatureblock = Block('Cryo Temperature', [
    BlockRow(
        Field(dev='T', name='CCI 3He'),
    ),
    BlockRow(
        Field(plot='Temperature', name='CCI 3He', dev='T_cci3he02_pot', width=60,
              height=40, plotwindow=3600),
    ),
    ],
    setups='ccr7',
)

_batteryblock = Block('Furnace Temperature', [
    BlockRow(
        Field(dev='T', name='Furnace'),
    ),
    BlockRow(
        Field(plot='Temperature', name='Furnace', dev='T', width=50, height=30,
              plotwindow=3600),
    ),
    ],
    setups='battery',
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

_amagnetblock = SetupBlock('amagnet')

_flipperblock = SetupBlock('mezeiflip')

_lockinblock = Block('Lock-In', [
    BlockRow(
        Field(dev='sr850[0]', name='X (V)', format='%1.6f', width=12),
        Field(dev='sr850[1]', name='Y (V)', format='%1.6f', width=12),
    ),
    BlockRow(
        Field(dev='sr850[2]', name='abs (V)', format='%1.6f', width=12),
        Field(dev='sr850[3]', name='phase (deg)', width=12),
    ),
    BlockRow(
        Field(plot='Lock-In', name='X', dev='sr850[0]', width=40, height=20,
              plotwindow=1*3600),
        Field(plot='Lock-In', name='Y', dev='sr850[1]'),
    ),
    ],
    setups='sr850',
)

_monochromatorblock = SetupBlock('monochromator')

_ngiblock = SetupBlock('ngi')

_cryomanipulatorblock = SetupBlock('cryomanipulator')

# generic Cryo-stuff
cryos = []
cryosupps = []
cryoplots = []
cryonames = ['cci3he01', 'cci3he02', 'cci3he03', 'cci3he10', 'cci3he11',
             'cci3he12', 'ccidu01', 'ccidu02']
for cryo in cryonames:
    suffix = 'pot' if cryo.startswith('cci3he') else 'mc'
    cryos.append(SetupBlock(cryo))
    cryosupps.append(SetupBlock(cryo, 'pressures'))
    cryoplots.append(
        Block(cryo.title(), [
            BlockRow(
                Field(plot=cryo, plotwindow=3600, width=50, height=30,
                      key=f't_{cryo}_{suffix}/setpoint'),
                Field(plot=cryo, plotwindow=3600, width=50, height=30,
                      dev=f't_{cryo}_{suffix}'),
                # Field(widget='nicos.guisupport.plots.TrendPlot',
                #       plotwindow=3600, width=25, height=25,
                #       devices=['t_%s/setpoint' % cryo, 't_%s' % cryo],
                #       names=['Setpoint', 'Regulation'],
                # ),
            ),
            ],
            setups=cryo,
        )
    )


_leftcolumn = Column(
    _shutterblock,
    _basicblock,
    _temperatureblock,
    _rscblock,
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
    _amagnetblock,
    _batteryblock,
    _sockets6block,
    _sockets7block,
    _ngiblock,
    _tensileblock
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        description = 'Status Display',
        title = 'ANTARES Status Monitor',
        filename = '/control/status.html',
        loglevel = 'info',
        interval = 10,
        cache = 'antareshw.antares.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Monospace',
        fontsize = 15,
        padding = 5,
        layout = [[_expcolumn], [_detectorikonlcolumn], [_detectorneocolumn],
                  [_detectorzwo01column],[_live],
                  [_leftcolumn, _rightcolumn]],
        noexpired = True,
    ),
)
