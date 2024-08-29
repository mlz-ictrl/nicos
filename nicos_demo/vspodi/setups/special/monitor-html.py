description = 'setup for the status HTML monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
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
)

_sc = Column(
    Block('Sample Changer', [
        BlockRow(Field(dev='sams'),),
    ],
    setups='samplechanger',
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'SPODI status monitor',
        loglevel = 'info',
        interval = 10,
        filename = 'webroot/index.html',
        cache = configdata('config_data.cache_host'),
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        prefix = 'nicos/',
        padding = 0,
        fontsize = 24,
        layout = [
            Row(_expcolumn),
            Row(_frm, _instrument, _sampletable),
            Row(_sc),
        ],
    ),
)
