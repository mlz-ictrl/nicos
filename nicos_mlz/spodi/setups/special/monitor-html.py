# This setup file configures the nicos status monitor.

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
                 Field(name='O2 part', dev='o2part_nguide'),),
    ],
    ),
)

_cryo = Column(
    Block('CCR', [
          BlockRow(Field(dev='T_ccr11_A'),
                   Field(dev='T_ccr11_B'),
                   Field(dev='T_ccr11_C'),
                   Field(dev='T_ccr11_D')),
    ],
    setups='ccr1*',
    ),
)

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

_newport = Column(
    Block('Newport', [
        BlockRow(Field(dev='sth_newport01')),
    ],
    ),
)

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
            Row(_cryo, _htf,),
            Row(_tension),
            Row(_magnet, _e,),
            Row(_sc, _newport),
        ],
    ),
)
