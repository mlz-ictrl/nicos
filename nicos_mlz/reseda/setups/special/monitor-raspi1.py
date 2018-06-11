description = 'setup for the right status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=30,
                       istext=True, maxlen=15),
                 Field(name='Sample',   key='sample/samplename', width=20,
                       istext=True, maxlen=15),
                 #Field(name='Current status', key='exp/action', width=30,
                 #      istext=True),
                 Field(name='Last file', key='exp/lastscan'),
                 Field(name='EchoTime', key='echotime', unit='ns'),
                 Field(name='Wavelength', dev='selector_lambda', unit='A')),
        ],
        setups='selector',
    ),
)

_column1 = Column(
    Block('Attenuators', [
        BlockRow(Field(name='att0', dev='att0'),
                 Field(name='att1', dev='att1'),
                 Field(name='att2', dev='att2')),
        ],
        setups='attenuators',
    ),
    Block('Slits', [
        BlockRow(Field(name='Pinhole 5', dev='pinhole5', unit='mm'),
                 Field(name='Pinhole 10', dev='pinhole10', unit='mm'),
                 Field(name='Slit 10x40', dev='slit', unit='mm')),
        ],
        setups='slits',
    ),
    Block('Environment', [
        BlockRow(Field(name='Power', dev='ReactorPower', format='%.1f', width=6),
                 Field(name='6-fold', dev='Sixfold', min='open', width=6)),
                 #Field(dev='NL5S', min='open', width=6),
                 #Field(dev='UBahn', width=5, istext=True, unit=' '),
                 #Field(dev='OutsideTemp', name='Temp', width=4, unit=' '),
        BlockRow(#Field(dev='DoseRate', name='Rate', width=6),
                 #Field(dev='Cooling', width=6),
                 #Field(dev='CoolTemp', name='CoolT', width=6, format='%.1f', unit=' '),
                 #Field(dev='PSDGas', width=6),
                 #Field(dev='ar', name='PSD Ar', width=4, format='%.1f', unit=' '),
                 #Field(dev='co2', name='PSD CO2', width=4, format='%.1f', unit=' '),
                 #Field(dev='t_in_fak40', name='FAK40', width=6, format='%.1f', unit=' '),
                 Field(dev='Crane', width=7)),
        ],
        setups='reactor and guidehall',
    ),
    Block('Pressures', [
        BlockRow(Field(name='Guides and Tube', dev='P_ng_elements', unit='mbar'),
                 Field(name='Polariser', dev='P_polarizer', units='mbar'),
                 Field(name='Selector', dev='P_selector_vacuum', units='mbar')),
        ],
        setups='pressure'
    ),
)

_column2 = Column(
    Block('Sample slits', [
        #BlockRow(Field(dev='slit1', name='Entrance slit', width=24, istext=True)),
        BlockRow(Field(dev='slit2', name='Sample slit', width=24, istext=True)),
        ],
        setups='slitsng',
    ),
    Block('Sample table', [
        BlockRow(Field(name='Rotation', dev='srz', unit='deg')),
        BlockRow('stx', 'sty'),
        BlockRow('sgx', 'sgy'),
        ],
        setups='sampletable',
    ),
    Block('arms', [
        BlockRow(Field(name='arm1', dev='arm1_rot', unit='deg'),
                 Field(name='arm2', dev='arm2_rot', unit='deg')),
        ],
     ),
)

ccrs = []
for i in range(10, 22 + 1):
    ccrs.append(Block('CCR%d' % i, [
        BlockRow(
            Field(name='Setpoint', key='t_ccr%d/setpoint' % i,
                   unitkey='t/unit'),
            Field(name='Target', key='t_ccr%d/target' % i,
                   unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power Stick',
                  key='t_ccr%d_stick/heaterpower' % i, format='%.3f',
                  unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power Tube',
                  key='t_ccr%d_tube/heaterpower' % i, format='%.3f',
                  unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='P1 ', dev='ccr%d_p1' % i, format='%.3f'),
        ),
        BlockRow(
             Field(name='A', dev='T_ccr%d_A' % i),
             Field(name='B', dev='T_ccr%d_B' % i),
        ),
        BlockRow(
             Field(name='C', dev='T_ccr%d_C' % i),
             Field(name='D', dev='T_ccr%d_D' % i),
        ),
        ],
        setups='ccr%d' % i,
    ))

cryos = []
for cryo in 'cci3he1 cci3he2 cci3he3 ccidu1 ccidu2'.split():
    cryos.append(Block(cryo.title(), [
        BlockRow(
            Field(name='Setpoint', key='t_%s/setpoint' % cryo,
                   unitkey='t/unit'),
            Field(name='Target', key='t_%s/target' % cryo,
                   unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power', key='t_%s/heaterpower' % cryo,
                   unitkey='t/unit'),
        ),
        BlockRow(
             Field(name='A', dev='T_%s_A' % cryo),
             Field(name='B', dev='T_%s_B' % cryo),
        ),
        ],
        setups=cryo,
    ))

_ccmsans = Block('SANS-1 5T Magnet', [
    BlockRow(Field(name='Field', dev='b_ccmsans', width=12)),
    BlockRow(Field(name='Target', key='b_ccmsans/target', width=12),
             Field(name='Asymmetry', key='b_ccmsans/asymmetry', width=12),
    ),
    BlockRow(Field(name='Power Supply 1', dev='a_ccmsans_left', width=12),
             Field(name='Power Supply 2', dev='a_ccmsans_right', width=12),
    ),
    ],
    setups='ccmsans',
)

_miramagnet = Block('MIRA 0.5T Magnet', [
    BlockRow(Field(name='Field', dev='B_miramagnet', width=12),
             Field(name='Target', key='B_miramagnet/target', width=12),
    ),
    BlockRow(Field(name='Current', dev='I_miramagnet', width=12)),
    ],
    setups='miramagnet',
)

_amagnet = Block('Antares Magnet', [
    BlockRow(Field(name='Field', dev='B_amagnet', width=12),
             Field(name='Target', key='B_amagnet/target', width=12),
    ),
    BlockRow(
             Field(name='Current', dev='amagnet_current', width=12),
             Field(name='ON/OFF', dev='amagnet_onoff', width=12),
    ),
    BlockRow(
             Field(name='Polarity', dev='amagnet_polarity', width=12),
             Field(name='Connection', dev='amagnet_connection', width=12),
    ),
    BlockRow(
             Field(name='Lambda out', dev='l_out', width=12),
    ),
    ],
    setups='amagnet',
)

_ccm2a = Block('CCM2a Magnet', [
    BlockRow(
             Field(name='Field', dev='B_ccm2a', width=12),
            ),
    BlockRow(
             Field(name='Target', key='B_ccm2a/target', width=12),
             Field(name='Readback', dev='B_ccm2a_readback', width=12),
            ),
    BlockRow(
             Field(name='T1', dev='ccm2a_T1', width=12),
             Field(name='T2', dev='ccm2a_T2', width=12),
            ),
    BlockRow(
             Field(name='TA', dev='ccm2a_TA', width=12),
             Field(name='TB', dev='ccm2a_TB', width=12),
            ),
    ],
    setups='ccm2a',
)

magnets = [_ccm2a, _ccmsans, _miramagnet, _amagnet]

_column3 = Column(
    Block('Cascade detector', [
        BlockRow(Field(name='ROI',   key='psd_channel[0]', format='%.0f', width=9),
                 Field(name='Total', key='psd_channel[1]', format='%.0f', width=9),
                 Field(name='MIEZE', key='psd_channel[2]', format='%.3f', width=6),
                 Field(name='Last image', key='exp/lastpoint')),
        BlockRow('timer', 'monitor1' ),
        BlockRow(Field(dev='mon_hv', width=6)),
                 #Field(dev='PSDHV', width=5),
                 #Field(dev='dtx')),
        ],
        setups='det_cascade and det_base',
    ),
    Block('Cryostat', [
        #BlockRow(
        #    Field(widget='nicos.guisupport.plots.TrendPlot', devices='T', names='T',  plotwindow=7200)),
        BlockRow(
            Field(name='T' ,key='T', unit='K'),
            Field(name='Ts', key='Ts', unit='K'),
            Field(name='Pressure', key='P_ccr', unit='mbar')),
        ],
        setups='alias_T and ccr'
        ),
) + Column(*magnets) + Column(*ccrs) + Column(*cryos)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'RESEDA MIEZE',
        loglevel = 'info',
        cache = 'resedahw2.reseda.frm2',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Consolas',
        fontsize = '14',
        padding = 2,
        layout = [[_expcolumn], [_column1, _column2, _column3]]
    ),
)
