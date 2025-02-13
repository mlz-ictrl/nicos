description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
                 Field(name='Current status', key='exp/action', width=90,
                       istext=True, maxlen=90),
                 Field(name='Last file', key='exp/lastpoint'),
                 Field(name='Current Sample', key='sample/samplename', width=26),
                ),
        ],
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='selector_rpm', dev='selector_rpm', width=16),
                 Field(name='selector_lambda', dev='selector_lambda', width=16),
                 ),
        BlockRow(
                 Field(name='selector_ng', dev='selector_ng', width=16),
                 Field(name='selector_tilt', dev='selector_tilt', width=16),
                ),
        BlockRow(
                 Field(name='water flow', dev='selector_wflow', width=16),
                 Field(name='rotor temp.', dev='selector_rtemp', width=16),
                ),
        ],
    ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
                 # Field(name='Col Pump', dev='coll_pump'),
                 Field(name='Col Tube', dev='coll_tube'),
                 Field(name='Col Nose', dev='coll_nose'),
                 Field(name='Det Nose', dev='det_nose'),
                 Field(name='Det Tube', dev='det_tube'),
                 ),
        ],
    ),
)

_table = Column(
    Block('Sample Table', [
        BlockRow(
                 Field(name='st1_phi', dev='st1_phi', width=13),
                 Field(name='st1_y', dev='st1_y', width=13),
                 ),
        BlockRow(
                 Field(name='st1_chi', dev='st1_chi', width=13),
                  Field(name='st1_z', dev='st1_z', width=13),
                ),
        BlockRow(
                 Field(name='st1_omg', dev='st1_omg', width=13),
                 Field(name='st1_x', dev='st1_x', width=13),
                ),
        ],
        setups='sample_table',
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
                 Field(name='T in', dev='t_in_memograph', width=12),
                 Field(name='T out', dev='t_out_memograph', width=12),
                 Field(name='Cooling', dev='cooling_memograph', width=12),
                ),
        BlockRow(
                 Field(name='Flow in', dev='flow_in_memograph', width=12),
                 Field(name='Flow out', dev='flow_out_memograph', width=12),
                 Field(name='Leakage', dev='leak_memograph', width=12),
                ),
        BlockRow(
                 Field(name='P in', dev='p_in_memograph', width=12),
                 Field(name='P out', dev='p_out_memograph', width=12),
                 Field(name='Crane Pos', dev='Crane', width=12),
                ),
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
                 Field(name='t', dev='det1_timer', width=13),
                 Field(name='t preset', key='det1_timer/preselection', width=13),
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
                 Field(name='bs1', dev='bs1', width=13),
                 Field(name='bs1_shape', dev='bs1_shape', width=13),
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
                 Field(dev='att', name='att', width=12),
                 ),
        BlockRow(
                 Field(dev='ng_pol', name='ng_pol', width=12),
                ),
        ],
    ),
)

_sanscolumn = Column(
    Block('Collimation',[
        BlockRow(
                 Field(dev='bg1', name='bg1', width=12),
                 Field(dev='bg2', name='bg2', width=12),
                 Field(dev='sa1', name='sa1', width=12),
                 Field(dev='sa2', name='sa2', width=12),
                ),
        BlockRow(
                 Field(dev='col', name='col', unit='m', format = '%.1f',
                       width=12),
                ),
        ],
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

_p_filter = Column(
    Block('Pressure Water Filter FAK40', [
        BlockRow(
                 Field(name='P in', dev='p_in_filter', width=12, unit='bar'),
                 Field(name='P out', dev='p_out_filter', width=12, unit='bar'),
                 Field(name='P diff', dev='p_diff_filter', width=12, unit='bar'),
                ),
        ],
    ),
)

_julabo = Column(
    Block('Julabo', [
        BlockRow(
            Field(name='Intern', dev='T_julabo_intern'),
            Field(name='Extern', dev='T_julabo_extern'),
        ),
        ],
        setups='julabo',
    ),
)

_julabo_plot = Column(
    Block('Julabo plot', [
        BlockRow(
                 Field(plot='julabo 30min', name='T intern 30min',
                       dev='T_julabo_intern', width=60, height=40,
                       plotwindow=1800),
                 Field(plot='julabo 30min', name='T extern 30min',
                       dev='T_julabo_extern'),
                 Field(plot='julabo 12h', name='T intern 12h',
                       dev='T_julabo_intern', width=60, height=40,
                       plotwindow=12*3600),
                 Field(plot='julabo 12h', name='T extern 12h',
                       dev='T_julabo_extern'),
        ),
        ],
        setups='julabo',
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
            Field(name='Data (lin)', picture='live_lin.png',
                  width=64, height=64),
            Field(name='Data (log)', picture='live_log.png',
                  width=64, height=64),
        ),
        ],
    ),
)

_col_slit = Column(
    Block('Slit Positions', [
        BlockRow(
                 Field(name='Top', dev='slit_top', unit='mm', format='%.2f',
                       width=12),
                ),
        BlockRow(
                 Field(name='Left', dev='slit_left', unit='mm', format='%.2f',
                       width=12),
                 Field(name='Right', dev='slit_right', unit='mm', format='%.2f',
                       width=12),
                ),
        BlockRow(
                 Field(name='Bottom', dev='slit_bottom', unit='mm',
                       format='%.2f', width=12),
                ),
        BlockRow(
                 Field(name='Slit [width x height]', dev='slit', unit='mm'),
                ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'SANS-1 Status monitor',
        filename = 'webroot/index.html',
        interval = 10,
        loglevel = 'info',
        cache = configdata('config_data.cache_host'),
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [
            Row(_expcolumn),
            Row(_sans1general, _table, _sans1det),
            Row(_pressurecolumn, _p_filter),
            Row(_selcolumn, _col_slit, _atpolcolumn, _sanscolumn),
            Row(_sc1, _sc2, _sc_t, _ccmsanssc, _julabo, _tisane_counts),
            Row(_julabo_plot),
            Row(_live),
        ],
    ),
)
