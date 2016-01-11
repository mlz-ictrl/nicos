description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=70,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='det/lastfilenumber'),
                 Field(name='Current Sample', key='sample/samplename', width=16),
            )
        ],
        # setups='experiment',
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='selector_rpm', dev='selector_rpm', width=8),
                ),
        BlockRow(
                 Field(name='selector_lambda', dev='selector_lambda', width=8),
                ),
        BlockRow(
                 Field(name='selector_ng', dev='selector_ng', width=8),
                ),
        BlockRow(
                 Field(name='selector_tilt', dev='selector_tilt', width=8),
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

_sans1general = Column(
    Block('General', [
        BlockRow(
                 Field(name='Reactor', dev='ReactorPower', width=8),
                 Field(name='6 Fold Shutter', dev='Sixfold', width=8),
                 Field(name='NL4a', dev='NL4a', width=8),
#               ),
#       BlockRow(
                 Field(name='T in', dev='t_in_memograph', width=8, unit='C'),
                 Field(name='T out', dev='t_out_memograph', width=8, unit='C'),
                 Field(name='Cooling', dev='cooling_memograph', width=8, unit='kW'),
#               ),
#       BlockRow(
                 Field(name='Flow in', dev='flow_in_memograph', width=8, unit='l/min'),
                 Field(name='Flow out', dev='flow_out_memograph', width=8, unit='l/min'),
                 Field(name='Leakage', dev='leak_memograph', width=8, unit='l/min'),
#               ),
#       BlockRow(
                 Field(name='P in', dev='p_in_memograph', width=8, unit='bar'),
                 Field(name='P out', dev='p_out_memograph', width=8, unit='bar'),
                 Field(name='Crane Pos', dev='Crane', width=8),
                ),
        ],
    ),
)

_collimationcolumn = Column(
    Block('Collimation',[
        BlockRow(
            Field(dev='att', name='att',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['x10','x100','x1000','OPEN'],
                  width=6.5,height=9),
            Field(dev='ng_pol', name='ng_pol',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','POL2','POL1','NG'],
                  width=5.5,height=9),
            Field(dev='col_20a', name='20a',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_20b', name='20b',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='bg1', name='bg1',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['50mm','OPEN','20mm','42mm'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
            Field(dev='col_16a', name='16a',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_16b', name='16b',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_12a', name='12a',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_12b', name='12b',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_8a', name='8a',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_8b', name='8b',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='bg2', name='bg2',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['28mm','20mm','12mm','OPEN'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
            Field(dev='col_4a', name='4a',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_4b', name='4b',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_2a', name='2a',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='col_2b', name='2b',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['LAS','free','COL','NG'],
                  width=5,height=9),
            Field(dev='sa1', name='sa1',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['20mm','10mm','50x50'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
        ),
        BlockRow(
            Field(dev='col', name='col'),
        ),
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
            Field(devices=['det1_z', 'det1_x','det1_omega', 'det_pos2'],
                  widget='nicos.sans1.monitorwidgets.Tube2', width=30, height=10)#, max=21000),
        ),
        BlockRow(
                 Field(name='det1_z', dev='det1_z', width=8, format='%i'),
                 Field(name='det1_x', dev='det1_x', width=8),
                 Field(name='det1_omg', dev='det1_omega', width=8),
                 Field(name='t', dev='det1_t_ist', width=8),
                 Field(name='t pres.', dev='det_1_t_soll', width=8),
                 Field(name='voltage', dev='det1_hv', width=8, format='%i'),
                 Field(name='mon 1', dev='det1_mon1', width=8),
                 Field(name='mon 2', dev='det1_mon2', width=8),
                 Field(name='bs1_x', dev='bs1_x', width=8, format='%.1f'),
                 Field(name='bs1_y', dev='bs1_y', width=8, format='%.1f'),
                ),
        ],
    ),
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'SANS-1 status monitor',
                     loglevel = 'debug',
#                    loglevel = 'info',
                     cache = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 15,#12
                     padding = 0,#3
                     layout = [
                                 Row(_selcolumn,_collimationcolumn),
                                 Row(_sans1det),
                                 #Row(_sans1general),
                                 Row(_pressurecolumn),
                                 Row(_expcolumn),
                               ],
                    ),
)
