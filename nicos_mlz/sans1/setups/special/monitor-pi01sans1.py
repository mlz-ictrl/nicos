description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=70,
                       istext=True, maxlen=100),
                 Field(name='Data file', key='exp/lastpoint'),
                 Field(name='Current Sample', key='sample/samplename', width=16,
                       istext=True),
            )
        ],
        # setups='experiment',
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='selector_rpm', dev='selector_rpm', width=12),
                ),
       BlockRow(
                 Field(name='selector_lambda', dev='selector_lambda', width=12),
                ),
       BlockRow(
                Field(name='selector_ng', dev='selector_ng', width=12),
                ),
       BlockRow(
                Field(name='selector_tilt', dev='selector_tilt', width=12, format = '%.1f'),
               ),
        BlockRow(
                 Field(name='water flow', dev='selector_wflow', width=12, format = '%.1f'),
                ),
       BlockRow(
                 Field(name='rotor temp.', dev='selector_rtemp', width=12, format = '%.1f'),
                ),
        ],
    ),
)

_tisane = Column(
    Block('Tisane', [
        BlockRow(
                 Field(name='DRU', dev='chopper_dru_rpm', width=12),
                ),
       BlockRow(
                 Field(name='Chopper 1', dev='chopper_ch1_speed', width=12, format = '%.1f'),
                ),
       BlockRow(
                Field(name='Chopper 2', dev='chopper_ch2_speed', width=12, format = '%.1f'),
                ),
       BlockRow(
                Field(name='Phase 1', dev='chopper_ch1_phase', width=12, format = '%.1f'),
               ),
        BlockRow(
                 Field(name='Phase 2', dev='chopper_ch2_phase', width=12, format = '%.1f'),
                ),
       BlockRow(
                 Field(name='water flow', dev='chopper_waterflow', width=12, format = '%.2'),
                ),
        ],
    setups='chopper',
    ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
                 Field(name='Col Pump', dev='coll_pump', width=11, format = '%g'),
                 Field(name='Col Tube', dev='coll_tube', width=11, format = '%g'),
                 Field(name='Col Nose', dev='coll_nose', width=11, format = '%g'),
                 Field(name='Det Nose', dev='det_nose', width=11, format = '%g'),
                 Field(name='Det Tube', dev='det_tube', width=11, format = '%g'),
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

_ubahncolumn = Column(
    Block('U-Bahn', [
        BlockRow(
                 Field(name='Train', dev='Ubahn', istext=True),
                ),
        ],
    ),
)

_collimationcolumn = Column(
    Block('Collimation',[
        BlockRow(
            Field(dev='att', name='att',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['dia10', 'x10','x100','x1000','open'],
                  width=6.5,height=9),
            Field(dev='ng_pol', name='23',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['col','pol2','pol1','ng'],
                  width=5.5,height=9),
            Field(dev='col_20a', name='20',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['las','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_20b', name='18',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='bg1', name='bg1',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['50mm','open','20mm','42mm'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
            Field(dev='col_16a', name='16',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_16b', name='14',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_12a', name='12',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_12b', name='10',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_8a', name='8',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_8b', name='6',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='bg2', name='bg2',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['28mm','20mm','12mm','open'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
            Field(dev='col_4a', name='4',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_4b', name='3',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_2a', name='2',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_2b', name='1.5',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='sa1', name='sa1',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['20mm','30mm','50x50'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
        ),
        BlockRow(
            Field(dev='col', name='col', unit='m', format = '%.1f'),
        ),
        ],
    ),
)

_sampleaperture = Column(
    Block('SA', [
        BlockRow(
                 Field(name='sa2', dev='sa2', width=8, format = '%g'),
                 )
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
            Field(devices=['det1_z', 'det1_x', 'det1_omg', 'det_pos2'],
                widget='nicos_mlz.sans1.gui.monitorwidgets.Tube2', width=30, height=10)#, max=21000),
        ),
        BlockRow(
                 Field(name='det1_z', dev='det1_z', width=12, unit='mm', format='%.0f'),
                 Field(name='det1_x', dev='det1_x', width=12, unit='mm', format='%.0f'),
                 Field(name='det1_omg', dev='det1_omg', width=12, unit='deg', format='%.0f'),
                 Field(name='t', dev='det1_t_ist', width=12),
                 Field(name='t pres.', key='det1_timer.preselection', width=12, unit='s', format='%i'),
                 Field(name='det1_hv', dev='det1_hv_ax', width=12, format='%i'),
                 Field(name='events', dev='det1_ev', width=12),
                 Field(name='mon 1', dev='det1_mon1', width=12),
                 Field(name='mon 2', dev='det1_mon2', width=12),
                 Field(name='bs1_x', dev='bs1_x', width=12, format='%.1f'),
                 Field(name='bs1_y', dev='bs1_y', width=12, format='%.1f'),
                ),
        ],
    ),
)

_p_filter = Column(
    Block('Pressure Water Filter FAK40', [
        BlockRow(
                 Field(name='P in filter', dev='p_in_filter', width=9.5, unit='bar'),
                 Field(name='P out filter', dev='p_out_filter', width=9.5, unit='bar'),
                 Field(name='P diff filter', dev='p_diff_filter', width=9.5, unit='bar'),
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
                 Field(name='Slit [width, height]', dev='slit', width=12, unit='mm'),
                ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = False,
        title = 'SANS-1 status monitor',
        loglevel = 'info',
        cache = 'sans1ctrl.sans1.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consola',
        fontsize = 12,#12
        padding = 0,#3
        layout = [
            Row(_selcolumn, _tisane, _col_slit, _collimationcolumn, _sampleaperture),
            Row(_sans1det),
            # Row(_sans1general),
            Row(_ubahncolumn, _pressurecolumn, _p_filter),
            Row(_expcolumn),
        ],
    ),
)
