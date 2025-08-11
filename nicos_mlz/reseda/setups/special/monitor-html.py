description = 'setup for the status monitor, HTML version'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            # Field(name='Title', key='exp/title', width=30, istext=True,
            #       maxlen=15),
            # Field(name='Sample', key='sample/samplename', width=20,
            #       istext=True, maxlen=15),
            Field(name='Last file', key='exp/lastscan'),
            Field(name='EchoTime', dev='echotime', unit='ns', width=15),
            Field(name='Wavelength', dev='selector_lambda', unit='A'),
        ),
        ],
        setups='selector and tuning',
    ),
)

_column1 = Column(
    Block('Cryostat', [
        BlockRow(
            Field(name='Setpoint', key='T_ccr_tube/setpoint',
                  unitkey='T/unit'),
            Field(name='Target', key='T_ccr_tube/target',
                  unitkey='T/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power Stick',
                  key='T_ccr_stick/heateroutput', format='%.3f',
                  unitkey='T/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power Tube',
                  key='T_ccr_tube/heateroutput', format='%.3f',
                  unitkey='T/unit'),
        ),
        BlockRow(
            Field(name='P ', dev='P_ccr', format='%.3f'),
        ),
        BlockRow(
             Field(name='A', dev='T_ccr_sample_stick_a'),
             Field(name='B', dev='T_ccr_sample_stick_b'),
        ),
        BlockRow(
             Field(name='C', dev='T_ccr_cold_head'),
             Field(name='D', dev='T_ccr_sample_tube'),
        ),
        BlockRow(
            Field(plot='cryo 30min', name='Temp 30min', devs='T_ccr_sample_tube',
                  width=60, height=40, plotwindow=1800),
        ),
        ],
        setups='ccr'
        ),
    Block('Environment', [
        BlockRow(
            Field(name='Power', dev='ReactorPower', format='%.1f', width=6),
            Field(name='6-fold', dev='Sixfold', min='open', width=6),
        ),
        BlockRow(
            # Field(dev='DoseRate', name='Rate', width=6),
            Field(dev='Crane', width=7),
        ),
        ],
        setups='reactor and guidehall',
    ),
    Block('Attenuators', [
        BlockRow(
            Field(name='att0', dev='att0'),
            Field(name='att1', dev='att1'),
            Field(name='att2', dev='att2'),
        ),
        ],
        setups='attenuators',
    ),
    # Block('Pressures', [
    #     BlockRow(
    #         Field(name='Guides and Tube', dev='P_ng_elements', unit='mbar'),
    #         Field(name='Polariser', dev='P_polarizer', units='mbar'),
    #         Field(name='Selector', dev='P_selector_vacuum', units='mbar'),
    #     ),
    #     ],
    #     setups='pressure'
    # ),
    Block('', [
        BlockRow(
            Field(name='Live data', picture='reseda-online/live.png',
                refresh=1, width=24, height=24),
        ),
        ]
    ),
)

_column2 = Column(
    Block('Sample slits', [
        BlockRow(
            Field(dev='slit1', name='Entrance slit', width=24, istext=True),
        ),
        BlockRow(
            Field(dev='slit2', name='Sample slit', width=24, istext=True),
        ),
        ],
        setups='slitsng',
    ),
    Block('Sample table', [
        # BlockRow(
        #     Field(name='Rotation', dev='srz', unit='deg'),
        # ),
        BlockRow(
            Field(dev='stx'),
            Field(dev='sty'),
            Field(dev='stz'),
        ),
        BlockRow(
            Field(dev='sgx'),
            Field(dev='sgy'),
            Field(dev='srz'),
        ),
        ],
        setups='sampletable',
    ),
    Block('arms', [
        BlockRow(
            Field(name='arm1', dev='arm1_rot', unit='deg'),
            Field(name='arm2', dev='arm2_rot', unit='deg'),
        ),
        ],
    ),
)

ccrs = [SetupBlock(ccr) for ccr in configdata('config_frm2.all_ccrs')]
cryos = [SetupBlock(cryo) for cryo in configdata('config_frm2.all_ccis')]

_ccm5h = SetupBlock('ccm5h')

_miramagnet = SetupBlock('miramagnet')

_amagnet = SetupBlock('amagnet')

_ccm2a2 = SetupBlock('ccm2a2')
_ccm2a2_temperature = SetupBlock('ccm2a2', 'temperatures')

magnets = [_ccm2a2, _ccm2a2_temperature, _ccm5h, _miramagnet, _amagnet]

_column3 = Column(
    Block('Cascade detector', [
        BlockRow(
            Field(name='ROI', key='psd_channel.roi', format='%.0f', width=15),
            Field(name='Last image', key='exp/lastpoint'),
        ),
        BlockRow(
            Field(name='cts ROI', key='psd/value[2]', format='%.0f', width=9),
            Field(name='Contrast ROI', key='psd/value[4]', format='%.2f',
                  width=9),
        ),
        BlockRow(
            Field(name='cts total', key='psd/value[3]', format='%.0f',
                  width=9),
            Field(name='Contrast total', key='psd/value[8]', format='%.2f',
                  width=9),
        ),
        BlockRow(
            Field(dev='timer'),
            Field(dev='monitor1'),
        ),
        BlockRow(
            Field(dev='mon_hv', width=9),
            Field(dev='det_hv', format='%.0f', width=9),
        ),
        BlockRow(
            Field(dev='psd_chop_freq', width=12),
            Field(dev='psd_timebin_freq', width=12),
        ),
        ],
        setups='det_cascade and det_base',
    ),
    Block('3He detector', [
        BlockRow(
            Field(name='Counts', key='det/value[2]', format='%.0f', width=12),
        ),
        BlockRow(
            Field(name='monitor', key='det/value[1]', format='%.0f', width=12),
        ),
        BlockRow(
            Field(name='timer', key='det/value[0]', format='%.0f', width=12),
        ),
        BlockRow(
            Field(dev='mon_hv', width=9),
            Field(dev='det_hv', format='%.0f', width=9),
        ),
        ],
        setups='det_3he and det_base',
    ),
) + Column(*magnets) + Column(*ccrs) + Column(*cryos)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'RESEDA status monitor',
        filename = '/control/webroot/index.html',
        loglevel = 'info',
        interval = 10,
        cache = 'resedactrl.reseda.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [[_expcolumn], [_column1, _column2, _column3]],
        noexpired = True,
    ),
)
