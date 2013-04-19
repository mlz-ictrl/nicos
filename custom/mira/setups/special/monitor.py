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
                 Field(name='Last file', key='filesink/lastfilenumber')),
    ]),
)

_column3 = Column(
    Block('Analyzer', [BlockRow('ath', 'att')], 'analyzer'),
    Block('Detector', [
        BlockRow('timer', 'mon2', 'ctr1'),
        BlockRow(Field(dev='det_fore', item=0, name='Forecast', format='%.2f'),
                 Field(dev='det_fore', item=2, name='Forecast', format='%d'),
                 Field(dev='det_fore', item=3, name='Forecast', format='%d')),
        BlockRow(Field(dev='MonHV', width=5),
                 Field(dev='DetHV', width=5)),
    ], '!cascade'),
    Block('Cascade', [
        BlockRow(Field(name='ROI',   key='psd/lastcounts', item=0, width=9),
                 Field(name='Total', key='psd/lastcounts', item=1, width=9),
                 #Field(name='MIEZE', key='psd/lastcontrast', item=0, format='%.3f', width=6),
                 Field(name='Last image', key='psd/lastfilenumber')),
        BlockRow('timer', 'mon2', 'ctr1'),
        BlockRow(Field(dev='MonHV', width=5),
                 Field(dev='PSDGas', width=6),
                 Field(dev='PSDHV', width=5),
                 Field(dev='dtx')),
    ], 'cascade'),
    Block('3He cell', [
        BlockRow(Field(name='Polarization', dev='pol', width=7),
                 Field(name='Guide field', dev='He_GF')),
    ], 'helios'),
    Block('MIEZE', [
        #BlockRow(Field(name='Setting', dev='mieze', item=0, istext=True),
        #         Field(name='Fourier time', dev='mieze', item=1, unit='ps'),
        #         Field(name='Tuning', key='mieze/tuning', istext=True)),
        BlockRow('freq1', 'amp1', 'coilamp1'),
        BlockRow('freq2', 'amp2', 'coilamp2'),
        BlockRow('fp1', 'fp2', 'rp1', 'rp2'),
        BlockRow('dc1', 'dc2', 'freq3', 'amp3'),
    ], 'mieze'),
#    Block('X-Z table axes', [BlockRow('mx', 'my')], 'gauss'),
    Block('TAS', [
        BlockRow(Field(name='H', dev='mira', item=0, format='%.3f', unit=' '),
                 Field(name='K', dev='mira', item=1, format='%.3f', unit=' '),
                 Field(name='L', dev='mira', item=2, format='%.3f', unit=' '),
                 Field(name='E', dev='mira', item=3, format='%.3f', unit=' ')),
        BlockRow(Field(name='Mode', key='mira/scanmode'),
                 Field(name='ki', dev='mono'), Field(name='kf', dev='ana'),
                 Field(name='Unit', key='mira/energytransferunit')),
    ], 'tas'),
    Block('Diffraction', [
        BlockRow(Field(name='H', dev='mira', item=0, format='%.3f', unit=' '),
                 Field(name='K', dev='mira', item=1, format='%.3f', unit=' '),
                 Field(name='L', dev='mira', item=2, format='%.3f', unit=' ')),
        BlockRow(Field(name='ki', dev='mono')),
    ], 'diff'),
    Block('CCR 11', [
        BlockRow(Field(name='Setpoint', key='t/setpoint', unitkey='t/unit'),
                 Field(name='Control', dev='T'), Field(dev='Ts', name='Sample')),
        BlockRow(Field(name='A', dev='T_ccr11_A'), Field(name='B', dev='T_ccr11_B'),
                 Field(name='C', dev='T_ccr11_C'), Field(name='D', dev='T_ccr11_D')),
        BlockRow(Field(name='P', key='t/p'), Field(name='I', key='t/i'),
                 Field(name='D', key='t/d'), Field(name='p', dev='ccr11_p1')),
    ], 'ccr11'),
    Block('MIRA Magnet', [BlockRow('I')], 'miramagnet'),
    Block('HV Stick', [BlockRow('HV')], 'hv_stick'),
    #Block('Temp. plot', [
    #    BlockRow(Field(plot='Temps', dev='T_ccr11_A', width=40),
    #             Field(plot='Temps', dev='T_ccr11_B'), Field(plot='Temps', dev='T_ccr11_C')),
    #], 'ccr5'),
)

_column2 = Column(
    Block('Slits', [
        BlockRow(Field(dev='ss1', name='Sample slit 1 (ss1)', width=24, istext=True)),
        BlockRow(Field(dev='ss2', name='Sample slit 2 (ss2)', width=24, istext=True)),
    ], 'slits'),
    Block('Sample', [
        BlockRow('om', 'srot', 'phi'),
        BlockRow('stx', 'sty', 'stz'),
        BlockRow('sgx', 'sgy'),
    ], 'sample'),
    Block('Eulerian cradle', [
        BlockRow('echi', 'ephi'),
        BlockRow(Field(dev='ec', name='Scattering plane', width=20, istext=True)),
    ], 'euler'),
    Block('Sample environment', [
        BlockRow(Field(name='Setpoint', key='t/setpoint', unitkey='t/unit'),
                 Field(name='A', dev='T_ccr5_A'), Field(name='B', dev='T_ccr5_B'),
                 Field(name='C', dev='T_ccr5_C')),
        BlockRow(Field(name='P', key='t/p'), Field(name='I', key='t/i'),
                 Field(name='D', key='t/d'), Field(name='p', dev='ccr5_p1')),
    ], 'ccr5'),
    Block('FRM Magnet', [
        BlockRow('B', Field(name='sth', dev='sth_m7T5_stick'),
                 Field(name='T1', dev='m7T5_T1', width=6),
                 Field(name='T2', dev='m7T5_T2', width=6)),
        BlockRow(Field(name='T3', dev='m7T5_T3', width=6),
                 Field(name='T4', dev='m7T5_T4', width=6),
                 Field(name='T8', dev='m7T5_T8', width=6)),
    ], 'magnet75'),
    Block('SANS-1 Magnet', [
        BlockRow('B', Field(name='T2', dev='m5T_T2', width=6),
                 Field(name='T3', dev='m5T_T3', width=6)),
        BlockRow(Field(name='T4', dev='m5T_T4', width=6),
                 Field(name='T5', dev='m5T_T5', width=6),
                 Field(name='T6', dev='m5T_T6', width=6)),
    ], 'magnet5'),
    Block('TTi + Huber', [
        BlockRow('dct1', 'dct2', Field(dev='flip', width=5)),
        BlockRow('tbl1', 'tbl2'),
    ], 'tti'),
    Block('Relays', [BlockRow('relay1', 'relay2')], 'relay'),
)

_column1 = Column(
    Block('MIRA1', [
        BlockRow('FOL', 'flip1'),
        BlockRow('mth', 'mtt'),
        BlockRow('mtx', 'mty'),
        BlockRow('mgx', 'mch'),
    ], 'mono1'),
    Block('MIRA2', [
        BlockRow('m2th', 'm2tt'),
        BlockRow('m2tx', 'm2ty', 'm2gx'),
        BlockRow('m2fv', Field(dev='atten1', width=4),
                 Field(dev='atten2', width=4), Field(dev='flip2', width=4)),
        BlockRow(Field(dev='lamfilter', width=4),
                 Field(dev='TBe', width=6), Field(dev='PBe', width=7)),
        BlockRow(Field(dev='ms2pos', width=4),
                 Field(dev='ms2', name='Mono slit 2 (ms2)', width=20, istext=True)),
    ], 'mono2'),
    Block('Environment', [
        BlockRow(Field(name='Power', dev='ReactorPower', format='%.1f', width=7),
                 Field(name='6-fold', dev='Sixfold', min='open', width=7),
                 Field(dev='NL6', min='open', width=7)),
        BlockRow(Field(dev='Shutter', width=7), Field(dev='Cooling', width=6),
                 Field(dev='CoolTemp', name='CoolT', width=6, format='%.1f', unit=' '),
                 Field(dev='Crane', min=10, width=7)),
    ], 'reactor'),
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
                     layout = [[_expcolumn], [_column1, _column2, _column3]])
)
