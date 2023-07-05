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
cryonames = ['cci3he01', 'cci3he02', 'cci3he03', 'cci3he10', 'ccidu01', 'ccidu02']
for cryo in cryonames:
    cryos.append(SetupBlock(cryo))
    cryosupps.append(SetupBlock(cryo, 'pressures'))
    cryoplots.append(SetupBlock(cryo, 'plots'))

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
