description = 'setup for the status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
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
                 Field(name='Last file', key='exp/lastscan')),
    ]),
)

_column1 = Column(
    Block('MIRA1 monochromator', [
        BlockRow('mth', 'mtt', 'mch', Field(dev='FOL', width=3)),
        BlockRow('mtx', 'mty', 'mgx', Field(dev='flip', width=3)),
    ], 'mono1'),
    Block('MIRA2 monochromator', [
        BlockRow(Field(dev='Shutter', width=7), 'm2th', 'm2tt'),
        BlockRow('m2tx', 'm2ty', 'm2gx'),
        BlockRow('m2fv', Field(dev='atten1', width=4),
                 Field(dev='atten2', width=4), Field(dev='flip2', width=4)),
        BlockRow(Field(dev='lamfilter', width=4),
                 Field(dev='TBe', width=6), #Field(dev='PBe', width=7),
                 Field(dev='Pccr', width=7)),
        BlockRow(Field(dev='ms2pos', width=4),
                 Field(dev='ms2', name='Mono slit 2 (ms2)', width=20, istext=True)),
    ], 'mono2'),
    Block('Environment', [
        BlockRow(Field(name='Power', dev='ReactorPower', format='%.1f', width=6),
                 Field(name='6-fold', dev='Sixfold', min='open', width=6),
                 Field(dev='NL6', min='open', width=6),
                 Field(dev='UBahn', width=5, istext=True, unit=' '),
                 Field(dev='OutsideTemp', name='Temp', width=4, unit=' ')),
        BlockRow(#Field(dev='DoseRate', name='Rate', width=6),
                 Field(dev='Cooling', width=6),
                 Field(dev='CoolTemp', name='CoolT', width=6, format='%.1f', unit=' '),
                 #Field(dev='PSDGas', width=6),
                 Field(dev='ar', name='PSD Ar', width=4, format='%.1f', unit=' '),
                 Field(dev='co2', name='PSD CO2', width=4, format='%.1f', unit=' '),
                 Field(dev='FAKTemp', name='FAK40', width=6, format='%.1f', unit=' '),
                 Field(dev='Crane', min=10, width=7)),
    ], 'reactor'),
)

_column2 = Column(
    Block('Sample slits', [
        BlockRow(Field(dev='ss1', name='Sample slit 1 (ss1)', width=24, istext=True)),
        BlockRow(Field(dev='ss2', name='Sample slit 2 (ss2)', width=24, istext=True)),
    ], 'slits'),
    Block('Sample table', [
        BlockRow('om', 'sth', 'phi'),
        BlockRow('stx', 'sty', 'stz'),
        BlockRow('sgx', 'sgy'),
    ], 'sample'),
    Block('Analyzer', [
        BlockRow('ath', 'att'),
    ], 'analyzer'),
)

_column3 = Column(
    Block('Detector', [
        BlockRow('timer', 'mon2', 'ctr1'),
        BlockRow(Field(dev='det_fore', item=0, name='Forecast', format='%.2f'),
                 Field(dev='det_fore', item=2, name='Forecast', format='%d'),
                 Field(dev='det_fore', item=3, name='Forecast', format='%d')),
        BlockRow(Field(dev='MonHV', width=5),
                 Field(dev='DetHV', width=5)),
    ], '!cascade'),
    Block('Cascade detector', [
        BlockRow(Field(name='ROI',   key='psd/lastcounts', item=0, width=9),
                 Field(name='Total', key='psd/lastcounts', item=1, width=9),
                 Field(name='MIEZE', key='psd/lastcontrast', item=0, format='%.3f', width=6),
                 Field(name='Last image', key='exp/lastimage')),
        BlockRow('timer', 'mon2', 'ctr1'),
        BlockRow(Field(dev='MonHV', width=5),
                 Field(dev='PSDHV', width=5),
                 Field(dev='dtx')),
    ], 'cascade'),
    Block('Diffraction', [
        BlockRow(Field(name='H', dev='mira', item=0, format='%.3f', unit=' '),
                 Field(name='K', dev='mira', item=1, format='%.3f', unit=' '),
                 Field(name='L', dev='mira', item=2, format='%.3f', unit=' ')),
        BlockRow(Field(name='ki', dev='mono'), Field(dev='lam', name='lambda'), Field(dev='Ei')),
    ], 'diff'),
    Block('TAS', [
        BlockRow(Field(name='H', dev='mira', item=0, format='%.3f', unit=' '),

                 Field(name='K', dev='mira', item=1, format='%.3f', unit=' '),
                 Field(name='L', dev='mira', item=2, format='%.3f', unit=' '),
                 Field(name='E', dev='mira', item=3, format='%.3f', unit=' ')),
        BlockRow(Field(name='Mode', key='mira/scanmode'),
                 Field(name='ki', dev='mono'), Field(name='kf', dev='ana'),
                 Field(name='Unit', key='mira/energytransferunit')),
    ], 'tas'),
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'MIRA Status monitor',
                     loglevel = 'info',
                     cache = 'mira1:14869',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,
                     padding = 5,
                     layout = [[_expcolumn], [_column1, _column2, _column3]]),
)
