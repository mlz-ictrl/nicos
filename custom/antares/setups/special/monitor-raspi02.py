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
    setups='detector',
    ),
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
    BlockRow(Field(plot='Temperature', name='Sensor B', dev='T_cc_B', width=40, height=20, plotwindow=3600),
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
        Field(dev='sr850', name='X', item=0),
        Field(dev='sr850', name='Y', item=1)
        ),
    ],
    setups='sr850',
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
    _selectorblock,
    _temperatureblock,
    _filterwheelblock,
    _sockets1block,
    _sockets2block,
    _sockets3block,
)

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

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                      description = 'Status Display',
                      title = 'raspi02',
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
