description = 'setup for the HTML status monitor'

includes = ['stdsystem']

_column1 = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=15,
                       istext=True, maxlen=15),
                 Field(name='Sample',   key='sample/samplename', width=15,
                       istext=True, maxlen=15),
                 Field(name='Remark',   key='exp/remark',   width=30,
                       istext=True, maxlen=30),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(key='exp/lastscan')),
        ],
    ),
)

_column2 = Column(
    Block('Instrument', [
        BlockRow('t_mth', 't_mtt'),
        BlockRow('t_ath', 't_att'),
        BlockRow(Field(dev='t_phi', width=4),
                 Field(dev='t_psi', width=4)),
        BlockRow(Field(dev='t_mono', width=4),
                 Field(dev='t_ana', name='Mono slit 2 (ms2)', width=20, istext=True)),
        ],
        setups='stdsystem',
    ),
    Block('Specials', [
        BlockRow(Field(picture='/some/pic.png')),
        BlockRow(Field(plot='plot', dev='t_mtt', plotwindow=3600)),
        ],
    ),
)


from test.utils import getCacheAddr

devices = dict(
    Monitor = device('test.test_simple.test_monitor_html.HtmlTestMonitor',
                     title = 'Status monitor',
                     filename = 'unused',
                     interval = 10,
                     cache = getCacheAddr(),
                     prefix = 'nicos/',
                     layout = [[_column1, _column2]]),
)
