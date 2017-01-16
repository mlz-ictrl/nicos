description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=50,
                       istext=True, maxlen=50),
                 Field(name='Last file', key='exp/lastpoint'),
                 Field(name='Current Sample', key='sample/samplename', width=16),
                ),
        ],
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='selector_rpm', dev='selector_rpm'),
                 Field(name='selector_lambda', dev='selector_lambda'),
                 ),
        BlockRow(
                 Field(name='selector_ng', dev='selector_ng'),
                 Field(name='selector_tilt', dev='selector_tilt'),
                ),
        BlockRow(
                 Field(name='water flow', dev='selector_wflow'),
                 Field(name='rotor temp.', dev='selector_rtemp'),
                ),
        ],
    ),
)

_ubahncolumn = Column(
    Block('U-Bahn', [
        BlockRow(
                 Field(name='Train', dev='Ubahn'),
                ),
        ],
    ),
)

_meteocolumn = Column(
    Block('Outside Temp', [
        BlockRow(
                 Field(name='Temp', dev='meteo'),
                ),
        ],
    ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
                 Field(name='Col Pump', dev='coll_pump'),
                 Field(name='Col Tube', dev='coll_tube'),
                 Field(name='Col Nose', dev='coll_nose'),
                 Field(name='Det Nose', dev='det_nose'),
                 Field(name='Det Tube', dev='det_tube'),
                 ),
        ],
    ),
)

_table2 = Column(
    Block('Sample Table 2', [
        BlockRow(
                 Field(name='st2_z', dev='st2_z', width=11),
                 ),
        BlockRow(
                 Field(name='st2_y', dev='st2_y', width=11),
                 ),
        BlockRow(
                 Field(name='st2_x', dev='st2_x', width=11),
                 ),
        ],
        setups='sample_table_2',
    ),
)

_table1 = Column(
    Block('Sample Table 1', [
        BlockRow(
                 Field(name='st1_phi', dev='st1_phi', width=11),
                 Field(name='st1_y', dev='st1_y', width=11),
                 ),
        BlockRow(
                 Field(name='st1_chi', dev='st1_chi', width=11),
                  Field(name='st1_z', dev='st1_z', width=11),
                ),
        BlockRow(
                 Field(name='st1_omg', dev='st1_omg', width=11),
                 Field(name='st1_x', dev='st1_x', width=11),
                ),
        ],
        setups='sample_table_1',
    ),
)

_sans1general = Column(
    Block('General', [
        BlockRow(
                 Field(name='Reactor', dev='ReactorPower', width=12),
                 Field(name='6 Fold Shutter', dev='Sixfold', width=12),
                 Field(name='NL4a', dev='NL4a', width=12),
                ),
        BlockRow(
                 Field(name='T in', dev='t_in_memograph', width=12, unit='C'),
                 Field(name='T out', dev='t_out_memograph', width=12, unit='C'),
                 Field(name='Cooling', dev='cooling_memograph', width=12, unit='kW'),
                ),
        BlockRow(
                 Field(name='Flow in', dev='flow_in_memograph', width=12, unit='l/min'),
                 Field(name='Flow out', dev='flow_out_memograph', width=12, unit='l/min'),
                 Field(name='Leakage', dev='leak_memograph', width=12, unit='l/min'),
                ),
        BlockRow(
                 Field(name='P in', dev='p_in_memograph', width=12, unit='bar'),
                 Field(name='P out', dev='p_out_memograph', width=12, unit='bar'),
                 Field(name='Crane Pos', dev='Crane', width=12),
                ),
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
                 Field(name='t', dev='det1_t_ist', width=13),
                 Field(name='t preset', key='det1_timer.preselection', width=13),
                ),
        BlockRow(
                 Field(name='det1_hv', dev='det1_hv_ax', width=13),
                 Field(name='det1_z', dev='det1_z', width=13),
                ),
        BlockRow(
                 Field(name='det1_omg', dev='det1_omg', width=13),
                 Field(name='det1_x', dev='det1_x', width=13),
                ),
        BlockRow(
                 Field(name='bs1_x', dev='bs1_x', width=13),
                 Field(name='bs1_y', dev='bs1_y', width=13),
                ),
        BlockRow(
                 Field(name='events', dev='det1_ev', width=13),
                ),
        BlockRow(
                 Field(name='mon 1', dev='det1_mon1', width=13),
                 Field(name='mon 2', dev='det1_mon2', width=13),
                ),
        ],
    ),
)

_atpolcolumn = Column(
    Block('Attenuator / Polarizer',[
        BlockRow(
                 Field(dev='att', name='att', width=7),
                 ),
        BlockRow(
                 Field(dev='ng_pol', name='ng_pol', width=7),
                ),
        ],
    ),
)

_sanscolumn = Column(
    Block('Collimation',[
        BlockRow(
                 Field(dev='bg1', name='bg1', width=5),
                 Field(dev='bg2', name='bg2', width=5),
                 Field(dev='sa1', name='sa1', width=5),
                 Field(dev='sa2', name='sa2', width=5),
                ),
        BlockRow(
                 Field(dev='col', name='col', unit='m'),
                ),
        ],
    ),
)

#~ _birmag = Column(
    #~ Block('17T Magnet', [
        #~ BlockRow(
                 #~ Field(name='helium level', dev='helevel_birmag', width=13),
                 #~ Field(name='field birmag', dev='field_birmag', width=13),
                #~ ),
        #~ BlockRow(
                 #~ Field(name='Setpoint 1 birmag', dev='sp1_birmag', width=13),
                 #~ Field(name='Setpoint 2 birmag', dev='sp2_birmag', width=13),
                #~ ),
        #~ BlockRow(
                 #~ Field(name='Temp a birmag', dev='ta_birmag', width=13),
                 #~ Field(name='Temp b birmag', dev='tb_birmag', width=13),
                #~ ),
        #~ ],
        #~ setups='!always!birmag',
    #~ ),
#~ )

_miramagnet = Column(
    Block('MIRA Magnet', [
        BlockRow(
                 Field(name='Field', dev='b_mira'),
                 Field(name='Target', key='b_mira/target', width=12),
                ),
        BlockRow(
                 Field(name='Current', dev='i', width=12),
                ),
        ],
        setups='miramagnet',
    ),
)

_amagnet = Column(
    Block('Antares Magnet', [
        BlockRow(
                 Field(name='Field', dev='B_amagnet'),
                 Field(name='Target', key='B_amagnet/target', width=12),
                ),
        ],
        setups='amagnet',
    ),
)

_sc1 = Column(
    Block('Sample Changer 1', [
         BlockRow(
            Field(name='Position', dev='sc1_y'),
            Field(name='SampleChanger', dev='sc1'),
        ),
        ],
        setups='sc1',
    ),
)

_sc2 = Column(
    Block('Sample Changer 2', [
         BlockRow(
            Field(name='Position', dev='sc2_y'),
            Field(name='SampleChanger', dev='sc2'),
        ),
        ],
        setups='sc2',
    ),
)

_sc_t = Column(
    Block('Temperature Sample Changer', [
         BlockRow(
            Field(name='Position', dev='sc_t_y'),
            Field(name='SampleChanger', dev='sc_t'),
        ),
        ],
        setups='sc_t',
    ),
)

_ccmsanssc = Column(
    Block('Magnet Sample Changer', [
         BlockRow(
            Field(name='Position', dev='ccmsanssc_axis'),
        ),
         BlockRow(
            Field(name='SampleChanger', dev='ccmsanssc_position', format='%i'),
        ),
         BlockRow(
            Field(name='Switch', dev='ccmsanssc_switch'),
        ),
        ],
        setups='ccmsanssc',
    ),
)

_htf03 = Column(
    Block('HTF03', [
        BlockRow(
            Field(name='Temperature', dev='T_htf03', format = '%.2f'),
            Field(name='Target', key='t_htf03/target', format = '%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_htf03/setpoint', format = '%.1f'),
            Field(name='Heater Power', key='t_htf03/heaterpower', format = '%.1f'),
        ),
        ],
        setups='htf03',
    ),
)

_htf03_plot = Column(
    Block('HTF03 plot', [
        BlockRow(
                 Field(plot='30 min htf03', name='30 min', dev='T_htf03', width=60, height=40, plotwindow=1800),
                 Field(plot='30 min htf03', name='Setpoint', dev='T_htf03/setpoint'),
                 Field(plot='30 min htf03', name='Target', dev='T_htf03/target'),
                 Field(plot='12 h htf03', name='12 h', dev='T_htf03', width=60, height=40, plotwindow=12*3600),
                 Field(plot='12 h htf03', name='Setpoint', dev='T_htf03/setpoint'),
                 Field(plot='12 h htf03', name='Target', dev='T_htf03/target'),
        ),
        ],
        setups='htf03',
    ),
)

_htf01 = Column(
    Block('HTF01', [
        BlockRow(
            Field(name='Temperature', dev='T_htf01', format = '%.2f'),
            Field(name='Target', key='t_htf01/target', format = '%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_htf01/setpoint', format = '%.1f'),
            Field(name='Heater Power', key='t_htf01/heaterpower', format = '%.1f'),
        ),
        ],
        setups='htf01',
    ),
)

_p_filter = Column(
    Block('Pressure Water Filter FAK40', [
        BlockRow(
                 Field(name='P in', dev='p_in_filter', width=9.5, unit='bar'),
                 Field(name='P out', dev='p_out_filter', width=9.5, unit='bar'),
                 Field(name='P diff', dev='p_diff_filter', width=9.5, unit='bar'),
                ),
        ],
    ),
)

_ccmsans = Column(
    Block('SANS-1 5T Magnet', [
        BlockRow(Field(name='Field', dev='b_ccmsans', width=12),
                ),
        BlockRow(
                 Field(name='Target', key='b_ccmsans/target', width=12),
                 Field(name='Asymmetry', key='b_ccmsans/asymmetry', width=12),
                ),
        BlockRow(
                 Field(name='Power Supply 1', dev='a_ccmsans_left', width=12),
                 Field(name='Power Supply 2', dev='a_ccmsans_right', width=12),
                ),
        ],
        setups='ccmsans',
    ),
)

_ccmsans_temperature = Column(
    Block('SANS-1 5T Magnet Temperatures', [
        BlockRow(
                 Field(name='CH Stage 1', dev='ccmsans_T1', width=12),
                 Field(name='CH Stage 2', dev='ccmsans_T2', width=12),
                ),
        BlockRow(
                 Field(name='Shield Top', dev='ccmsans_T3', width=12),
                 Field(name='Shield Bottom', dev='ccmsans_T4', width=12),
                ),
        BlockRow(
                 Field(name='Magnet TL', dev='ccmsans_T5', width=12),
                 Field(name='Magnet TR', dev='ccmsans_T6', width=12),
                ),
        BlockRow(
                 Field(name='Magnet BL', dev='ccmsans_T8', width=12),
                 Field(name='Magnet BR', dev='ccmsans_T7', width=12),
                ),
        ],
        setups='ccmsans',
    ),
)

_ccmsans_plot = Column(
    Block('SANS-1 5T Magnet plot', [
        BlockRow(
                 Field(plot='30 min ccmsans', name='30 min', dev='B_ccmsans', width=60, height=40, plotwindow=1800),
                 Field(plot='30 min ccmsans', name='Target', dev='b_ccmsans/target'),
                 Field(plot='12 h ccmsans', name='12 h', dev='B_ccmans', width=60, height=40, plotwindow=12*3600),
                 Field(plot='12 h ccmsans', name='Target', dev='b_ccmsans/target'),
        ),
        ],
        setups='ccmsans',
    ),
)

_ccr19_plot = Column(
    Block('30min T and Ts plot', [
        BlockRow(
                 Field(plot='30 min ccr19', name='T', dev='T', width=60, height=40, plotwindow=1800),
                 Field(plot='30 min ccr19', name='Ts', dev='Ts'),
                 Field(plot='30 min ccr19', name='Setpoint', dev='T/setpoint'),
                 Field(plot='30 min ccr19', name='Target', dev='T/target'),
        ),
        ],
        setups='ccr19',
    ),
)

_spinflipper = Column(
    Block('Spin Flipper', [
        BlockRow(
             Field(name='P', dev='P_spinflipper'),
        ),
        BlockRow(
             Field(name='Forward', key='P_spinflipper/forward', unitkey='W'),
             Field(name='Reverse', key='P_spinflipper/reverse', unitkey='W'),
        ),
        BlockRow(
             Field(name='Temperature', dev='T_spinflipper'),
             Field(name='Voltage', dev='U_spinflipper'),
        ),
        BlockRow(
             Field(name='A_spinflipper_hp', dev='A_spinflipper_hp'),
             Field(name='F_spinflipper_hp', dev='F_spinflipper_hp'),
        ),
        ],
        setups='spinflip',
    ),
)

newports = []
for k in [1,2,3,4,5,10,11,12]:
    newports.append(Block('NewPort%02d' % k, [
        BlockRow(
            Field(name='Position', dev='sth_newport%02d' % k,
                   unitkey='t/unit'),
        ),
        ],
        setups='newport%02d' % k,
    ))
_newports = Column(*tuple(newports))

ccrs = []
for i in range(10, 22 + 1):
    ccrs.append(Block('CCR%d' % i, [
        BlockRow(
                 Field(name='Setpoint', key='t_ccr%d_tube/setpoint' % i,
                       unitkey='t/unit'),
                 Field(name='Manual Heater Power', key='t_ccr%d_tube/heaterpower' % i,
                       unitkey=''),
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
_ccrs = Column(*tuple(ccrs))

cryos = []
for cryo in 'cci3he1 cci3he2 cci3he3 ccidu1 ccidu2'.split():
    cryos.append(Block(cryo.title(), [
        BlockRow(
                 Field(name='Setpoint', key='t_%s/setpoint' % cryo,
                       unitkey='t/unit'),
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
_cryos = Column(*tuple(cryos))

_julabo = Column(
    Block('Julabo', [
        BlockRow(
            Field(name='Intern', dev='T_intern'),
            Field(name='Extern', dev='T_extern'),
        ),
        ],
        setups='julabo',
    ),
)

_tisane_fg1 = Column(
    Block('TISANE Frequency Generator 1 - Sample', [
        BlockRow(
                Field(name='Frequency', key='tisane_fg1/frequency', format='%.2e', unit='Hz', width=12),
                ),
        BlockRow(
                Field(name='Amplitude', key='tisane_fg1/amplitude', format='%.2f', unit='V', width=12),
                Field(name='Offset', key='tisane_fg1/offset', format='%.2f', unit='V', width=12),
                ),
        BlockRow(
                Field(name='Shape', key='tisane_fg1/shape', width=12),
                Field(name='Dutycycle', key='tisane_fg1/duty', format='%i', unit='%', width=12),
                ),
        ],
        setups='tisane',
    ),
)

_tisane_fg2 = Column(
    Block('TISANE Frequency Generator 2 - Detector', [
        BlockRow(
                Field(name='Frequency', key='tisane_fg2/frequency', format='%.2e', unit='Hz', width=12),
                ),
        BlockRow(
                Field(name='Amplitude', key='tisane_fg2/amplitude', format='%.2f', unit='V', width=12),
                Field(name='Offset', key='tisane_fg2/offset', format='%.2f', unit='V', width=12),
                ),
        BlockRow(
                Field(name='Shape', key='tisane_fg2/shape', width=12),
                Field(name='Dutycycle', key='tisane_fg2/duty', format='%i', unit='%', width=12),
                ),
        ],
        setups='tisane',
    ),
)

_tisane_fc = Column(
    Block('TISANE Frequency Counter', [
        BlockRow(
                Field(name='Frequency', dev='tisane_fc', format='%.2e', width=12),
                ),
        ],
        setups='tisane',
    ),
)

_tisane_counts = Column(
    Block('TISANE Counts', [
        BlockRow(
                Field(name='Counts', dev='TISANE_det_pulses', width=12),
                ),
        ],
        setups='tisane',
    ),
)

_live = Column(
    Block('Live image of Detector', [
        BlockRow(
            Field(name='Data (lin)', picture='sans1-online/live_lin.png', width=64, height=64),
            Field(name='Data (log)', picture='sans1-online/live_log.png', width=64, height=64),
        ),
        ],
    ),
)

_col_slit = Column(
    Block('Slit Positions', [
        BlockRow(
                 Field(name='Top', dev='slit_top', unit='mm', format='%.2f'),
                ),
        BlockRow(
                 Field(name='Left', dev='slit_left', unit='mm', format='%.2f'),
                 Field(name='Right', dev='slit_right', unit='mm', format='%.2f'),
                ),
        BlockRow(
                 Field(name='Bottom', dev='slit_bottom', unit='mm', format='%.2f'),
                ),
        BlockRow(
                 Field(name='Slit width', dev='slit', unit='mm', format='%.2f'),
                ),
        ],
    ),
)

devices = dict(
    Monitor = device('services.monitor.html.Monitor',
                     title = 'SANS-1 Status monitor',
                     filename = '/sans1control/webroot/index.html',
                     interval = 10,
                     loglevel = 'info',
                     cache = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 17,
                     layout = [
                                 Row(_expcolumn),
                                 Row(_sans1general, _table2, _table1,
                                     _sans1det),
                                 Row(_ubahncolumn, _meteocolumn, _pressurecolumn, _p_filter),
                                 Row(_selcolumn, _col_slit, _atpolcolumn, _sanscolumn),
                                 Row(_ccmsans, _ccmsans_temperature,
                                     _spinflipper, _ccrs, _cryos, _sc1, _sc2, _sc_t,
                                     _ccmsanssc, _miramagnet, _amagnet, _htf03, _htf01,
                                     _newports, _julabo, _tisane_counts, _tisane_fc,
                                     _tisane_fg1, _tisane_fg2),
                                 Row(_ccmsans_plot, _ccr19_plot, _htf03_plot),
                                 Row(_live),
                               ],
                    ),
)
