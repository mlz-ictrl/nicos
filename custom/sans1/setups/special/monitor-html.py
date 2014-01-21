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
                       istext=True, maxlen=40),
                 Field(name='Last file', key='det/lastfilenumber'),
                ),
        ],
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='Sel NG', dev='sel_ng_sw'),
                 Field(name='Sel tilt', dev='sel_tilt'),
                ),
        ],
    ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
                 Field(name='Col Pump', dev='coll_p3'),
                 Field(name='Col Tube', dev='coll_p1'),
                 Field(name='Col Nose', dev='coll_p2'),
                 Field(name='Det Nose', dev='tub_p2'),
                 Field(name='Det Tube', dev='tub_p1'),
                 ),
        ],
    ),
)

_table = Column(
    Block('Sample Table', [
        BlockRow(
                 Field(name='z-2a', dev='z_2a'),
                 Field(name='y-2a', dev='y_2a'),
                 Field(name='x-2a', dev='x_2a'),
                ),
        BlockRow(
                 Field(name='phi-2b', dev='phi_2b'),
                 Field(name='chi-2b', dev='chi_2b'),
                 Field(name='omega-2b', dev='omega_2b'),
                ),
        BlockRow(
                 Field(name='y-2b', dev='y_2b'),
                 Field(name='z-2b', dev='z_2b'),
                 Field(name='x-2b', dev='x_2b'),
                ),
        ],
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
                 Field(name='t ist da', dev='det1_t_ist', width=13),
                 Field(name='t set', dev='det_1_t_soll', width=13),
                ),
        BlockRow(
                 Field(name='Voltage', dev='hv', width=13),
                 Field(name='det1_z-1a', dev='det1_z1a', width=13),
                ),
        BlockRow(
                 Field(name='det1_omg-1a', dev='det1_omega1a', width=13),
                 Field(name='det1_x-1a', dev='det1_x1a', width=13),
                ),
        BlockRow(
                 Field(name='bs1_x-1a', dev='bs1_x1a', width=13),
                 Field(name='bs1_y-1a', dev='bs1_y1a', width=13),
                ),
        ],
    ),
)

_atpolcolumn = Column(
    Block('Attenuator / Polarizer',[
        BlockRow(
                 Field(dev='at', name='Att', width=7),
                 Field(dev='ng_pol', name='Pol', width=7),
                ),
        ],
    ),
)

_sanscolumn = Column(
    Block('SANS',[
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

_birmag = Column(
    Block('17T Magnet', [
        BlockRow(
                 Field(name='helium level', dev='helevel_birmag', width=13),
                 Field(name='field birmag', dev='field_birmag', width=13),
                ),
        BlockRow(
                 Field(name='Setpoint 1 birmag', dev='sp1_birmag', width=13),
                 Field(name='Setpoint 2 birmag', dev='sp2_birmag', width=13),
                ),
        BlockRow(
                 Field(name='Temp a birmag', dev='ta_birmag', width=13),
                 Field(name='Temp b birmag', dev='tb_birmag', width=13),
                ),
        ], 'birmag'
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
                                 Row(_sans1general, _table, _sans1det),
                                 Row(_selcolumn, _pressurecolumn),
                                 Row(_atpolcolumn, _sanscolumn),
                                 Row(_birmag),
                               ],
                    ),
)
