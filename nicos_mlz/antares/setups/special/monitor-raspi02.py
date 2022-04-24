#  -*- coding: utf-8 -*-

description = 'setup for the status monitor'
group = 'special'

_detectorcolumn = Column(
    Block('Detector', [
        BlockRow(
            Field(name='Path', key='Exp/proposalpath', width=40, format='%s/'),
            Field(name='Last Image', key='ccd.lastfilename', width=50),
        ),
        BlockRow(
            Field(name='CCD status', key='ccd/status[1]', width=25),
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
        setups='detector',
    ),
)

_live = Block('Live image of Detector', [
        BlockRow(
            # Field(picture='webroot/live_lin.png',
            Field(picture='liveimage_internal/live_lin.png',
                  width=50, height=50,refresh=10),
        ),
    ],
    setups='liveimage_internal',
)

_sockets1block = SetupBlock('sockets', 'cabinet1')

_sockets2block = SetupBlock('sockets', 'cabinet2')

_sockets3block = SetupBlock('sockets', 'cabinet3')

_sockets6block = SetupBlock('sockets', 'cabinet6')

_sockets7block = SetupBlock('sockets', 'cabinet7')

_filterwheelblock = SetupBlock('rm_filterwheel')

_selectorblock = SetupBlock('selector')

_temperatureblock = Block('Cryo Temperature', [
    BlockRow(
        Field(dev='T'),
        Field(dev='Ts')
    ),
    BlockRow(
        Field(plot='Temperature', name='T', dev='T', width=40, height=20,
              plotwindow=3600),
    ),
    ],
    setups='cc_puma',
)

_garfieldblock = Block('Garfield Magnet', [
    BlockRow(
        Field(dev='B_amagnet', name='B'),
        Field(dev='amagnet_symmetry', name='Mode')
    ),
    ],
    setups='amagnet',
)

_flipperblock = SetupBlock('mezeiflip')

_lockinblock = SetupBlock('sr850')

_monochromatorblock = SetupBlock('monochromator')

_ngiblock = SetupBlock('ngi')

_cryomanipulatorblock = SetupBlock('cryomanipulator')

# generic Cryo-stuff
cryos = []
cryosupps = []
cryoplots = []
cryodict = dict(cci3he01='3He-insert', cci3he02='3He-insert', cci3he03='3He-insert',
                ccidu01='Dilution-insert', ccidu02='Dilution-insert')
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
	_live,
	_selectorblock,
    _temperatureblock,
    _filterwheelblock,
    _sockets1block,
    _sockets2block,
    _sockets3block,
)

_leftcolumn += Column(*cryos) + Column(*cryosupps)

_rightcolumn = Column(
    _cryomanipulatorblock,
    _monochromatorblock,
    _flipperblock,
    _lockinblock,
    _garfieldblock,
    _sockets6block,
    _sockets7block,
    _ngiblock,
)

_rightcolumn += Column(*cryoplots)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        description = 'Status Display',
        title = 'C3PO',
        loglevel = 'info',
        cache = 'antareshw.antares.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        fontsize = 15,
        valuefont = 'Monospace',
        padding = 5,
        layout = [[_detectorcolumn],[_leftcolumn, _rightcolumn]],
    ),
)
