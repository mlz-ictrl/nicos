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
    BlockRow(Field(dev='T'), Field(dev='Ts')),
    BlockRow(Field(plot='Temperature', name='T', dev='T', width=40, height=20, plotwindow=3600),
        ),
    ],
    setups=['ccr7'],
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
        Field(dev='sr850[0]', name='X'),
        Field(dev='sr850[1]', name='Y')
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
    _selectorblock,
#    _temperatureblock,
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
    _ngi_jcnsblock,
)

_rightcolumn += Column(*cryoplots)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
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
