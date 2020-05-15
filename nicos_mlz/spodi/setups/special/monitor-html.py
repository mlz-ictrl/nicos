description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
                 # Field(name='Proposal', key='exp/proposal', width=7),
                 # Field(name='Title',    key='exp/title',    width=20,
                 #       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Data file', key='exp/lastpoint'))]),
)

_sampletable = Column(
    Block('Sample table', [
        BlockRow(Field(dev='omgs')),
        BlockRow(Field(dev='tths')),
    ],
    ),
)

_instrument = Column(
    Block('Instrument', [
        BlockRow(Field(dev='wav')),
        BlockRow(Field(dev='slits')),
        BlockRow(Field(dev='mon'),
                 Field(name='Resosteps', key='adet/resosteps'),
                 Field(name='Step', key='adet/value[0]'),),
    ],
    ),
)

_frm = Column(
    Block('FRM II', [
        BlockRow(Field(dev='ReactorPower',)),
    ],
    ),
    Block('SPODI', [
        BlockRow(Field(name='O2', dev='o2_nguide'),
                 Field(name='O2 part', dev='o2part_nguide'),
                 ),
        BlockRow(Field(name='p1 N-Guide', dev='p1_nguide'),
                 Field(name='p2 N-Guide', dev='p2_nguide'),
                 Field(name='p3 N-Guide', dev='p3_nguide'),
                 ),
    ],
    ),
)

# generic CCR-stuff
ccrs = []
ccrsupps = []
ccrplots = []
_ccrnrs = [6,] + list(range(10, 22 + 1))
for i in _ccrnrs:
    ccrs.append(
        Block('CCR%d-Pulse tube' % i, [
            BlockRow(
                Field(dev='t_ccr%d_c' % i, name='Coldhead'),
                Field(dev='t_ccr%d_d' % i, name='Regulation'),
                Field(dev='t_ccr%d_b' % i, name='Sample'),
            ),
            BlockRow(
                Field(key='t_ccr%d/setpoint' % i, name='Setpoint'),
                Field(key='t_ccr%d/p' % i, name='P', width=7),
                Field(key='t_ccr%d/i' % i, name='I', width=7),
                Field(key='t_ccr%d/d' % i, name='D', width=6),
            ),
            ],
            setups='ccr%d and not cci3he*' % i,
        )
    )
    ccrsupps.append(
        Block('CCR%d' % i, [
            BlockRow(
                Field(dev='T_ccr%d_A' % i, name='A'),
                Field(dev='T_ccr%d_B' % i, name='B'),
                Field(dev='T_ccr%d_C' % i, name='C'),
                Field(dev='T_ccr%d_D' % i, name='D'),
            ),
            BlockRow(
                Field(key='t_ccr%d/setpoint' % i, name='SetP.', width=6),
                Field(key='t_ccr%d/p' % i, name='P', width=4),
                Field(key='t_ccr%d/i' % i, name='I', width=4),
                Field(key='t_ccr%d/d' % i, name='D', width=3),
            ),
            BlockRow(
                Field(dev='ccr%d_p1' % i, name='P1'),
                Field(dev='ccr%d_p2' % i, name='P2'),
            ),
            ],
            setups='ccr%d' % i,
        )
    )




_cryo = Column(*ccrs)

_cryosup = Column(*ccrsupps)


_htf = Column(
    Block('HTF', [
        BlockRow(Field(dev='T'),
                 Field(name='Power', key='T/heaterpower'),)
    ],
    setups='htf*',
    ),
)

_magnet = Column(
    Block('Magnet', [
        BlockRow(Field(dev='B')),
    ],
    setups='ccm*',
    ),
)

_sc = Column(
    Block('Sample Changer', [
        BlockRow(Field(dev='sams'),),
    ],
    setups='samplechanger',
    ),
)

_e = Column(
    Block('E field', [
        BlockRow(Field(dev='E')),
    ],
    setups='efield',
    ),
)

_tension = Column(
    Block('Tension rack', [
        BlockRow(Field(dev='teload'),
                 Field(dev='tepos'),
                 Field(dev='teext'),
                 Field(dev='topos'),
                 Field(dev='tomom'),),
    ],
    setups='tensile',
    ),
)

_nps =[1,2,3,10,11,12]
_npblocks = []

for i in _nps:
    _npblocks.append(    Block('Newport', [
        BlockRow(Field(dev='sth_newport%02d' % i)),
    ],
    setups='newport%02d' % i,
    ),
)
_newport = Column(*_npblocks)


devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'SPODI status monitor',
        loglevel = 'info',
        interval = 10,
        filename = '/spodicontrol/webroot/index.html',
        cache = 'spodictrl.spodi.frm2',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        prefix = 'nicos/',
        padding = 0,
        fontsize = 24,
        layout = [
            Row(_expcolumn),
            Row(_frm, _instrument, _sampletable),
            Row(_htf,),
            Row(_cryosup),
            Row(_tension),
            Row(_magnet, _e,),
            Row(_sc, _newport),
        ],
    ),
)
