description = 'setup for the HTML status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=50,
                       istext=True, maxlen=50),
                 Field(name='Last file', key='exp/lastimage'),
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
                 Field(name='selector_ng', dev='selector_ng'),
                 Field(name='selector_tilt', dev='selector_tilt'),
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
        ], 'sample_table_2'
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
        ], 'sample_table_1'
    ),
)

_sans1general = Column(
    Block('General', [
        BlockRow(
                 Field(name='Reactor', dev='ReactorPower', width=12, format = '%.2f', unit='MW'),
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
                 Field(name='Crane Pos', dev='Crane', width=12, unit='m'),
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
                 Field(name='det1_z-1a', dev='det1_z', width=13),
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
                 Field(name='mon 1', dev='det1_mon1', width=13),
                 Field(name='mon 2', dev='det1_mon2', width=13),
                ),
        ],
    ),
)

_atpolcolumn = Column(
    Block('Attenuator / Polarizer',[
        BlockRow(
                 Field(dev='att', name='atte', width=7),
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
        #~ ], '!always!birmag'
    #~ ),
#~ )

_ccmsans = Column(
    Block('Sans1 Magnet', [
        BlockRow(
                 Field(name='Field', dev='b_overall'),
                ),
        BlockRow(
                 Field(name='Power Supply 1', dev='b_left'),
                 Field(name='Power Supply 2', dev='b_right'),
                ),
        BlockRow(
                 Field(name='CH Stage 1', dev='t_1'),
                 Field(name='CH Stage 2', dev='t_2'),
                ),
        BlockRow(
                 Field(name='Shield Top', dev='t_3'),
                 Field(name='Shield Bottom', dev='t_4'),
                ),
        BlockRow(
                 Field(name='Magnet TL', dev='t_5'),
                 Field(name='Magnet TR', dev='t_6'),
                ),
        BlockRow(
                 Field(name='Magnet BL', dev='t_8'),
                 Field(name='Magnet BR', dev='t_7'),
                ),
        ],'sansmagnet'
    ),
)

_miramagnet = Column(
    Block('MIRA Magnet', [
        BlockRow(
                 Field(name='Field', dev='b_mira'),
                 Field(name='Target', key='b_mira/target', width=12),
                ),
        BlockRow(
                 Field(name='Current', dev='i', width=12),
                ),
        ],'miramagnet'
    ),
)

_amagnet = Column(
    Block('Antares Magnet', [
        BlockRow(
                 Field(name='Field', dev='B_amagnet'),
                 Field(name='Target', key='B_amagnet/target', width=12),
                ),
        ],'amagnet'
    ),
)

_sc1 = Column(
    Block('Sample Changer 1', [
      BlockRow(
       Field(name='Position', dev='sc1_y'),
       Field(name='SampleChanger', dev='sc1'),
       ),
], 'sc1'),)

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
], 'htf03'),)

_spinflipper = Column(
    Block('SpinFlipper', [
    BlockRow(
             Field(name='Power', dev='p_sf'),
             Field(name='Frequency', dev='f_sf'),
            ),
    BlockRow(
             Field(name='Forward', dev='forward_sf'),
             Field(name='Reverse', dev='reverse_sf'),
            ),
    BlockRow(Field(name='Temperature of AG1016', dev='t_sf'),),
    BlockRow(
             Field(name='Ampl HP33220a', dev='a_agilent1'),
             Field(name='Freq HP33220a', dev='f_agilent1'),
            ),
        ], 'sc1'
    ),
)

newports = []
for k in range(1, 3 + 1):
    newports.append(Block('NewPort0%d' % k, [
        BlockRow(
            Field(name='Position', dev='sth_newport0%d' % k,
                   unitkey='t/unit'),
        ),
    ], 'newport0%d' % k))
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
    ], 'ccr%d' % i))
_ccrs = Column(*tuple(ccrs))

cryos = []
for j in range(1, 5 + 1):
    cryos.append(Block('Cryo%d' % j, [
        BlockRow(
            Field(name='Setpoint', key='t_cryo%d/setpoint' % j,
                   unitkey='t/unit'),
            Field(name='Manual Heater Power', key='t_cryo%d/heaterpower' % j,
                   unitkey='t/unit'),
        ),
        BlockRow(
             Field(name='A', dev='T_cryo%d_A' % j),
             Field(name='B', dev='T_cryo%d_B' % j),
        ),
    ], 'cryo%d' % j))
_cryos = Column(*tuple(cryos))

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
                                 Row(_sans1general, _table2, _table1, _sans1det),
                                 Row(_ubahncolumn, _pressurecolumn),
                                 Row(_selcolumn, _atpolcolumn, _sanscolumn),
                                 Row(_ccmsans, _spinflipper, _ccrs, _cryos, _sc1, _miramagnet, _amagnet, _htf03, _newports),
                               ],
                    ),
)
