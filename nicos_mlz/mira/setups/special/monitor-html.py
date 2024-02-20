description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title', key='exp/title', width=15, istext=True,
                  maxlen=15),
            Field(name='Sample',   key='sample/samplename', width=15,
                  istext=True, maxlen=15),
            Field(name='Remark',   key='exp/remark',   width=30,
                  istext=True, maxlen=30),
            Field(name='Current status', key='exp/action', width=30,
                  istext=True),
            Field(name='Last file', key='exp/lastscan'),
        ),
        ],
    ),
)

_column3 = Column(
    Block('Analyzer', [
        BlockRow(
            Field(dev='ath'),
            Field(dev='att'),
        ),
        ],
        setups='analyzer',
    ),
    Block('Detector', [
        BlockRow(
            Field(dev='timer'),
            Field(dev='mon2'),
            Field(dev='ctr1'),
            Field(dev='ctr2'),
        ),
        BlockRow(
            Field(dev='det_fore[0]', name='Forecast', format='%.2f'),
            Field(dev='det_fore[2]', name='Forecast', format='%d'),
            Field(dev='det_fore[3]', name='Forecast', format='%d'),
        ),
        BlockRow(
            Field(dev='MonHV', width=5),
            Field(dev='DetHV', width=5),
            Field(dev='VetoHV', width=5),
        ),
        ],
        setups='not cascade',
    ),
    Block('Cascade', [
        BlockRow(
            Field(name='ROI',   key='psd/lastcounts[0]', width=9),
            Field(name='Total', key='psd/lastcounts[1]', width=9),
            Field(name='MIEZE', key='psd/lastcontrast[0]', format='%.3f',
                  width=6),
            Field(name='Last image', key='exp/lastpoint'),
        ),
        BlockRow(
            Field(dev='timer'),
            Field(dev='mon2'),
            Field(dev='ctr1'),
            Field(dev='ctr2'),
        ),
        BlockRow(
            Field(dev='MonHV', width=5),
            Field(dev='PSDGas', width=6),
            Field(dev='PSDHV', width=5),
            Field(dev='dtx'),
            Field(dev='VetoHV', width=5),
        ),
        ],
        setups='cascade',
    ),
    SetupBlock('ccm2a2'), SetupBlock('ccm2a2', 'temperatures'),
    Block('MIEZE', [
        BlockRow(
            Field(name='Echotime', dev='echotime', unit='ns', width=22),
        ),
        BlockRow(
            Field(dev='hrf1'),
            Field(name='freq1', dev='cbox1_fg_freq'),
            Field(name='amp1', dev='cbox1_fg_amp'),
            Field(name='coil1', dev='cbox1_coil_rms'),
        ),
        BlockRow(
            Field(dev='hrf2'),
            Field(name='freq2', dev='cbox2_fg_freq'),
            Field(name='amp2', dev='cbox2_fg_amp'),
            Field(name='coil2', dev='cbox2_coil_rms'),
        ),
        BlockRow(
            Field(name='fp1', dev='cbox1_fwdp'),
            Field(name='fp2', dev='cbox2_fwdp'),
            Field(name='rp1', dev='cbox1_revp'),
            Field(name='rp2', dev='cbox2_revp'),
        ),
        BlockRow(
            Field(dev='hsf1'),
            Field(dev='sf1'),
            Field(dev='hsf2'),
            Field(dev='sf2'),
        ),
        BlockRow(
            Field(name='f_chop', dev='psd_chop_freq', format='%g'),
            Field(name='f_timebin', dev='psd_timebin_freq', format='%g'),
        ),
        ],
        setups='mieze'
    ),
    # Block('X-Z table axes', [
    #     BlockRow(
    #         'mx',
    #         'my',
    #     ),
    #     ],
    #     setups='gauss',
    # ),
    Block('TAS', [
        BlockRow(
            Field(name='H', dev='mira[0]', format='%.3f', unit=''),
            Field(name='K', dev='mira[1]', format='%.3f', unit=''),
            Field(name='L', dev='mira[2]', format='%.3f', unit=''),
            Field(name='E', dev='mira[3]', format='%.3f', unit=''),
        ),
        BlockRow(
            Field(name='Mode', key='mira/scanmode'),
            Field(name='ki', dev='mono'), Field(name='kf', dev='ana'),
            Field(name='Unit', key='mira/energytransferunit'),
        ),
        ],
        setups='tas',
    ),
    Block('Diffraction', [
        BlockRow(
            Field(name='H', dev='mira[0]', format='%.3f', unit=''),
            Field(name='K', dev='mira[1]', format='%.3f', unit=''),
            Field(name='L', dev='mira[2]', format='%.3f', unit=''),
        ),
        BlockRow(
            Field(name='ki', dev='mono'),
        ),
        ],
        setups='diff',
    ),
    Block('MIRA Magnet', [
        BlockRow(
            Field(dev='I_miramagnet'),
            Field(dev='B_miramagnet'),
        ),
        BlockRow(
            Field(name='T1', dev='miramagnet_T1', width=6, format='%.2f'),
            Field(name='T2', dev='miramagnet_T2', width=6, format='%.2f'),
        ),
        BlockRow(
            Field(name='T3', dev='miramagnet_T3', width=6, format='%.2f'),
            Field(name='T4', dev='miramagnet_T4', width=6, format='%.2f'),
        ),
        ],
        setups='miramagnet',
    ),
)

cryoblocks = []
for cryo in configdata('config_frm2.all_ccis'):
    cryoblocks.append(SetupBlock(cryo))
    cryoblocks.append(SetupBlock(cryo, 'pressures'))

_column2 = Column(*[
    Block('Slits', [
        BlockRow(
            Field(dev='ss1', name='Sample slit 1 (ss1)', width=24, istext=True),
        ),
        BlockRow(
            Field(dev='ss2', name='Sample slit 2 (ss2)', width=24, istext=True),
        ),
        ],
        setups='slits',
    ),
    Block('Sample', [
        BlockRow(
            Field(dev='sth'),
            Field(dev='sth_st'),
            Field(dev='stt'),
        ),
        BlockRow(
            Field(dev='stx'),
            Field(dev='sty'),
            Field(dev='stz'),
        ),
        BlockRow(
            Field(dev='sgx'),
            Field(dev='sgy'),
        ),
        ],
        setups='sample',
    ),
    Block('Eulerian cradle', [
        BlockRow(
            Field(dev='echi'),
            Field(dev='ephi'),
        ),
        # BlockRow(
        #     Field(dev='ec', name='Scattering plane', width=20, istext=True)
        # ),
        ],
        setups='euler',
    ),
    Block('Sample environment CCR11', [
        BlockRow(
            Field(name='Setpoint', key='t_ccr11/setpoint', unitkey='t_ccr11/unit'),
            Field(name='A', dev='T_ccr11_A'), Field(name='B', dev='T_ccr11_B'),
            Field(name='C', dev='T_ccr11_C'), Field(name='D', dev='T_ccr11_D'),
        ),
        BlockRow(
            Field(name='P', key='t_ccr11/p'), Field(name='I', key='t_ccr11/i'),
            Field(name='D', key='t_ccr11/d'), Field(name='p', dev='ccr11_p1'),
        ),
        ],
        setups='ccr11',
    ),
    Block('Cryostat (CCR21)', [
        BlockRow(
            Field(name='Setpoint', key='t/setpoint', unitkey='t/unit',
                  format='%.2f'),
            Field(name='Control', dev='T'), Field(dev='Ts', name='Sample'),
        ),
        BlockRow(
            Field(name='A', dev='T_ccr21_A'), Field(name='B', dev='T_ccr21_B'),
            Field(name='C', dev='T_ccr21_C'), Field(name='D', dev='T_ccr21_D'),
        ),
        BlockRow(
            Field(name='P', key='t/p'), Field(name='I', key='t/i'),
            Field(name='D', key='t/d'), Field(name='p', dev='ccr21_p1'),
        ),
        ],
        setups='ccr21',
    ),
    Block('Furnace (IRF01)', [
        BlockRow(
            Field(name='Setpoint', key='t_irf01/setpoint', unitkey='t_irf01/unit',
                  format='%.2f'),
            Field(name='Temp', dev='T_irf01'),
        ),
        BlockRow(
            Field(name='P', key='t_irf01/p'),
            Field(name='I', key='t_irf01/i'),
            Field(name='D', key='t_irf01/d'),
        ),
        BlockRow(
            Field(name='Heater power', key='t_irf01/heaterpower', unit='%',
                  format='%.2f'),
        ),
        ],
        setups='irf01',
    ),
    Block('Furnace (HTF20)', [
        BlockRow(
            Field(name='Setpoint', key='t_htf20/setpoint', unitkey='t_htf20/unit',
                  format='%.2f'),
            Field(name='Temp', dev='T_htf20'),
        ),
        BlockRow(
            Field(name='P', key='t_htf20/p'),
            Field(name='I', key='t_htf20/i'),
            Field(name='D', key='t_htf20/d'),
        ),
        BlockRow(
            Field(name='Heater output', key='t_htf20/heateroutput', unit='%',
                  format='%.2f'),
            Field(name='Vacuum', dev='htf20_vacuum'),
        ),
        ],
        setups='htf20',
    ),
    ] + cryoblocks + [
    SetupBlock('ccm5v5'), SetupBlock('ccm5v5', 'temperatures'),
    SetupBlock('ccm5h'), SetupBlock('ccm5h', 'temperatures'),
    Block('TTi + Huber', [
        BlockRow(
            Field(dev='dct1'),
            Field(dev='dct2'),
            Field(dev='flip', width=5),
        ),
        BlockRow(
            Field(dev='tbl1'),
            Field(dev='tbl2'),
        ),
        ],
        setups='mezeiflip',
    ),
    Block('Relays', [
        BlockRow(
            Field(dev='relay1'),
            Field(dev='relay2'),
        ),
        ],
        setups='relay',
    ),
    ]
)

_column1 = Column(
    Block('Environment', [
        BlockRow(
            Field(name='Power', dev='ReactorPower', width=7),
            Field(name='6-fold', dev='Sixfold', min='open', width=7),
            Field(dev='NL6', min='open', width=7),
        ),
        BlockRow(
            Field(dev='Shutter', width=7),
            Field(dev='Cooling', width=6),
            Field(dev='CoolTemp', width=6, format='%.1f', unit=" "),
            Field(dev='t_in_fak40', name='FAK40', width=6, format='%.1f',
                  unit=' '),
        ),
        BlockRow(
            Field(dev='ar', name='PSD Ar', width=4, format='%.1f', unit=' '),
            Field(dev='co2', name='PSD CO2', width=4, format='%.1f', unit=' '),
            Field(dev='Crane', min=10, width=7),
        ),
        ],
    ),
    Block('MIRA1', [
        BlockRow(
            Field(dev='FOL'),
            Field(dev='flip1'),
        ),
        BlockRow(
            Field(dev='m1th'),
            Field(dev='m1tt'),
        ),
        BlockRow(
            Field(dev='m1tx'),
            Field(dev='m1ty'),
        ),
        BlockRow(
            Field(dev='m1gx'),
            Field(dev='m1ch'),
        ),
        ],
        setups='mono1',
    ),
    Block('MIRA2', [
        BlockRow(
            Field(dev='m2th'),
            Field(dev='m2tt'),
        ),
        BlockRow(
            Field(dev='m2tx'),
            Field(dev='m2ty'),
            Field(dev='m2gx'),
        ),
        BlockRow(
            Field(dev='m2fv'),
            Field(dev='atten1', width=4),
            Field(dev='atten2', width=4),
            Field(dev='flip2', width=4),
        ),
        BlockRow(
            Field(dev='lamfilter', width=4),
            Field(dev='TBe', width=6),
            Field(dev='PBe', width=7),
        ),
        BlockRow(
            Field(dev='ms2pos', width=4),
            Field(dev='ms2', name='Mono slit 2 (ms2)', width=20, istext=True),
        ),
        ],
        setups='mono2',
    ),
)

_column4 = Column(
    SetupBlock('ccm5v5', 'plots'),
    Block('Magnet temp. plots', [
        BlockRow(
            Field(dev='ccm5h_T_stage2', name='T2', plot='Tm5', plotwindow=24*3600,
                  width=100, height=40),
            Field(dev='ccm5h_T_shield_top', name='T3', plot='Tm5'),
            Field(dev='ccm5h_T_shield_bottom', name='T4', plot='Tm5'),
            Field(dev='ccm5h_T_topleft', name='T5', plot='Tm5'),
            Field(dev='ccm5h_T_topright', name='T6', plot='Tm5'),
        ),
        ],
        setups='ccm5h',
    ),
)


devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'MIRA Status monitor',
        filename = '/miracontrol/status.html',
        interval = 30,
        loglevel = 'info',
        cache = 'miractrl.mira.frm2.tum.de:14869',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [[_expcolumn], [_column1, _column2, _column3], [_column4]],
        noexpired = True,
    ),
)
