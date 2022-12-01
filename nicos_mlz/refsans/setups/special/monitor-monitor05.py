# coding: utf-8


description = 'Facility Managing [05]'

group = 'special'

_shgacol = Column(
    Block('gamma', [
        BlockRow(
            Field(name='position', dev='shutter_gamma_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='shutter_gamma_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='shutter_gamma_acc', width=8),
        ),
        ],
    ),
)
_nok2col = Column(
    Block('nok2', [
        BlockRow(
            Field(name='position', dev='nok2r_motor', width=8),
            Field(name='position', dev='nok2s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='nok2r_analog', width=8),
            Field(name='poti_pos', dev='nok2s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='nok2r_acc', width=8),
            Field(name='accuracy', dev='nok2s_acc', width=8),
        ),
        ],
    ),
)
_nok3col = Column(
    Block('nok3', [
        BlockRow(
            Field(name='position', dev='nok3r_motor', width=8),
            Field(name='position', dev='nok3s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='nok3r_analog', width=8),
            Field(name='poti_pos', dev='nok3s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='nok3r_acc', width=8),
            Field(name='accuracy', dev='nok3s_acc', width=8),
        ),
        ],
    ),
)
_nok4col = Column(
    Block('nok4', [
        BlockRow(
            Field(name='position', dev='nok4r_motor', width=8),
            Field(name='position', dev='nok4s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='nok4r_analog', width=8),
            Field(name='poti_pos', dev='nok4s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='nok4r_acc', width=8),
            Field(name='accuracy', dev='nok4s_acc', width=8),
        ),
        ],
    ),
)
_nok6col = Column(
    Block('nok6', [
        BlockRow(
            Field(name='position', dev='nok6r_motor', width=8),
            Field(name='position', dev='nok6s_motor', width=8),
            ),
        BlockRow(
            Field(name='poti_pos', dev='nok6r_analog', width=8),
            Field(name='poti_pos', dev='nok6s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='nok6r_acc', width=8),
            Field(name='accuracy', dev='nok6s_acc', width=8),
        ),
        ],
    ),
)
_nok7col = Column(
    Block('nok7', [
        BlockRow(
            Field(name='position', dev='nok7r_motor', width=8),
            Field(name='position', dev='nok7s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='nok7r_analog', width=8),
            Field(name='poti_pos', dev='nok7s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='nok7r_acc', width=8),
            Field(name='accuracy', dev='nok7s_acc', width=8),
        ),
        ],
    ),
)
_nok8col = Column(
    Block('nok8', [
        BlockRow(
            Field(name='position', dev='nok8r_motor', width=8),
            Field(name='position', dev='nok8s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='nok8r_analog', width=8),
            Field(name='poti_pos', dev='nok8s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='nok8r_acc', width=8),
            Field(name='accuracy', dev='nok8s_acc', width=8),
        ),
        ],
    ),
)
_nok9col = Column(
    Block('nok9', [
        BlockRow(
            Field(name='position', dev='nok9r_motor', width=8),
            Field(name='position', dev='nok9s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='nok9r_analog', width=8),
            Field(name='poti_pos', dev='nok9s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='nok9r_acc', width=8),
            Field(name='accuracy', dev='nok9s_acc', width=8),
        ),
        ],
    ),
)
_zb2col = Column(
    Block('zb2', [
        BlockRow(
            Field(name='position', dev='zb2_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='zb2_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='zb2_acc', width=8),
        ),
        ],
    ),
)
_zb3col = Column(
    Block('zb3', [
        BlockRow(
            Field(name='position', dev='zb3r_motor', width=8),
            Field(name='position', dev='zb3s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='zb3r_analog', width=8),
            Field(name='poti_pos', dev='zb3s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='zb3r_acc', width=8),
            Field(name='accuracy', dev='zb3s_acc', width=8),
        ),
        ],
    ),
)
_bs1col = Column(
    Block('bs1', [
        BlockRow(
            Field(name='position', dev='bs1r_motor', width=8),
            Field(name='position', dev='bs1s_motor', width=8),
        ),
        BlockRow(
            Field(name='poti_pos', dev='bs1r_analog', width=8),
            Field(name='poti_pos', dev='bs1s_analog', width=8),
        ),
        BlockRow(
            Field(name='accuracy', dev='bs1r_acc', width=8),
            Field(name='accuracy', dev='bs1s_acc', width=8),
        ),
        ],
    ),
)

_refcolumn = Column(
    Block('References', [
        BlockRow(
            Field(dev='nok_refa1', name='ref_A1'),
            Field(dev='nok_refa2', name='ref_A2'),
        ),
        BlockRow(
            Field(dev='nok_refb1', name='ref_B1'),
            Field(dev='nok_refb2', name='ref_B2'),
        ),
        BlockRow(
            Field(dev='nok_refc1', name='ref_C1'),
            Field(dev='nok_refc2', name='ref_C2'),
        ),
        ],
    ),
)
_memograph = Column(
    Block('memograph', [
        BlockRow(
            Field(name='flow_in', dev='flow_memograph_in'),
            Field(name='flow_out', dev='flow_memograph_out'),
            Field(name='diff', dev='leak_memograph'),
        ),
        BlockRow(
            Field(name='t_in', dev='t_memograph_in'),
            Field(name='t_out', dev='t_memograph_out'),
            Field(name='power', dev='cooling_memograph'),
        ),
        BlockRow(
            Field(name='p_in', dev='p_memograph_in'),
            Field(name='p_out', dev='p_memograph_out'),
        ),
        ],
    ),
    Block('Temperature', [
        BlockRow(
                Field(name='RACK3 so NL-Halle', dev='Temperature2', width=7),
        ),
        ],
    ),
)

Time_selection = [3,'h',60*60]
Elemente = [
          'sds',
      ]


_pumpstand = Column(
    Block('pumpstand', [
        BlockRow(
            Field(name='CB', dev='pressure_CB'),
            Field(name='SFK', dev='pressure_SFK'),
            Field(name='SR', dev='pressure_SR'),
        ),
        BlockRow(
            Field(name='CB', dev='pump_CB'),
            Field(name='SFK', dev='pump_SFK'),
            Field(name='SR', dev='pump_SR'),
        ),
        BlockRow(
            Field(name='CB', dev='chamber_CB'),
            Field(name='SFK', dev='chamber_SFK'),
            Field(name='SR', dev='chamber_SR'),
        ),
        ],
    ),
    Block('yoke_acc', [
        BlockRow(
                Field(name='acc of yoke', dev='det_yoke_acc', width=7),
        ),
        ],
    ),
    Block('yoke_acc', [
        BlockRow(
                Field(name='acc of yoke', dev='det_yoke_acc', width=7),
        ),
        ],
    ),
)

_05_chopper = Column(
    Block('chopper', [
        BlockRow(
            Field(name='Fatal', key='chopper/fatal', width=10),
            Field(name='cpt00', dev='cpt00'),
        ),
        BlockRow(
            Field(name='Fatal', key='chopper/fatal', width=10),
            Field(name='cpt01', dev='cpt01'),
        ),
        BlockRow(
            Field(name='conditon 1', key='chopper_speed/condition', width=10),
            Field(name='cpt1', dev='cpt1'),
        ),
        BlockRow(
            Field(name='conditon 2', key='chopper2/condition', width=10),
            Field(name='cpt2', dev='cpt2'),
        ),
        BlockRow(
            Field(name='conditon 3', key='chopper3/condition', width=10),
            Field(name='cpt3', dev='cpt3'),
        ),
        BlockRow(
            Field(name='conditon 4', key='chopper4/condition', width=10),
            Field(name='cpt4', dev='cpt4'),
        ),
        BlockRow(
            Field(name='conditon 5', key='chopper5/condition', width=10),
            Field(name='cpt5', dev='cpt5'),
        ),
        BlockRow(
            Field(name='conditon 6', key='chopper6/condition', width=10),
            Field(name='cpt6', dev='cpt6'),
        ),
        ],
    ),
)

_power = Column(
    Block('Power', [
        BlockRow(
            Field(name='USV', dev='PowerSupplyUSV', width=7),
            Field(name='Normal', dev='PowerSupplyNormal', width=7),
            #Field(name='Akku', dev='AkkuPower', width=7),
        ),
        ],
    ),
)
_air = Column(
    Block('Air', [
        BlockRow(
            Field(name='Air 1', dev='Air1Pressure', width=7),
            Field(name='Air 2', dev='Air2Pressure', width=7),
        ),
        ],
    ),
)
_vsd_chopper = Column(
    Block('Chopper', [
        BlockRow(
            Field(name='Enable', dev='ChopperEnable1', width=7),
            #Field(name='Enable', dev='ChopperEnable2', width=7),
            Field(name='Ext On', dev='ControllerStatus', width=7),
            Field(name='Ext Off', dev='TempVibration', width=7),
        ),
        ],
    ),
)
_temp = Column(
    Block('Temperatures', [
        BlockRow(
            #Field(name='temp', dev='Temperature1', width=7),
            Field(name='RACK3 so NL-Halle', dev='Temperature2', width=7),
            #Field(name='temp', dev='Temperature3', width=7),
            #Field(name='temp', dev='Temperature4', width=7),
            Field(name='choppermotor 1', dev='Temperature8', width=7),
            Field(name='choppermotor 2', dev='Temperature7', width=7),
            Field(name='choppermotor 3', dev='Temperature6', width=7),
            Field(name='choppermotor 4', dev='Temperature5', width=7),
        ),
        BlockRow(
            #Field(name='RACK3 so NL-Halle', dev='Temperature2', width=7),
            Field(name='choppercore 1', dev='core1', width=7),
            Field(name='choppercore 2', dev='core2', width=7),
            Field(name='choppercore 3', dev='core3', width=7),
            Field(name='choppercore 4', dev='core4', width=7),
        ),
        ],
    ),
)
w = 12
_cooling = Column(
    Block('cooling', [
        BlockRow(
            Field(name='press in', dev='Water1Pressure', width=w),
            Field(name='Flow 1', dev='Water1Flow', width=w),
            Field(name='Flow 2', dev='Water2Flow', width=w),
            Field(name='Flow 3', dev='Water3Flow', width=w),
            Field(name='Flow 4', dev='Water4Flow', width=w),
            Field(name='Flow 5', dev='Water5Flow', width=w),
        ),
        BlockRow(
            Field(name='press out', dev='Water2Pressure', width=w),
            Field(name='Temp 1', dev='Water1Temp', width=w),
            Field(name='Temp 2', dev='Water2Temp', width=w),
            Field(name='Temp 3', dev='Water3Temp', width=w),
            Field(name='Temp 4', dev='Water4Temp', width=w),
            Field(name='Temp 5', dev='Water5Temp', width=w),
        ),
        ],
    ),
)

con_width = 150
_place = Column(
    Block('place', [
        BlockRow(
            Field(name='place', dev='place', width=12),
            Field(name='', key='place/condition', width=con_width),
        ),
        BlockRow(
            Field(name='PO_safe', dev='PO_save', width=12),
            Field(name='', key='PO_save/condition', width=con_width),
        ),
        BlockRow(
            Field(name='SR_safe', dev='SR_save', width=12),
            Field(name='', key='SR_save/condition', width=con_width),
        ),
        BlockRow(
            Field(name='doors', dev='doors', width=12),
            Field(name='', key='doors/condition', width=con_width),
        ),
        ],
    ),
)

_signal = Column(
    Block('safetysystem', [
        BlockRow(
            Field(name='Everything', dev='signal', width=12),
            Field(name='', key='signal/condition', width=con_width),
        ),
        ],
    ),
)

_basis = Column(
    Block('basis', [
        BlockRow(
            Field(name='basis', dev='basis', width=12),
            Field(name='', key='basis/status[1]', width=con_width),
        ),
        ],
    ),
)

_service = Column(
    Block('service', [
        BlockRow(
            Field(name='service', dev='service', width=12),
            Field(name='', key='service/condition', width=con_width),
        ),
        ],
    ),
)
_supervisor = Column(
    Block('supervisor', [
        BlockRow(
            Field(name='supervisor', dev='supervisor', width=12),
            Field(name='', key='supervisor/condition', width=con_width),
        ),
        ],
    ),
)
_techOK = Column(
    Block('techOK', [
        BlockRow(
            Field(name='techOK', dev='techOK', width=12),
            Field(name='', key='techOK/condition', width=con_width),
        ),
        ],
    ),
)
_user = Column(
    Block('user', [
        BlockRow(
            Field(name='user', dev='user', width=12),
            Field(name='', key='user/condition', width=con_width),
        ),
        ],
    ),
)

_personalkey = Column(
    Block('personalkey', [
        BlockRow(
            Field(name='personalkey', dev='personalkey', width=12),
            Field(name='', key='personalkey/status[1]', width=con_width),
        ),
        ],
    ),
)

_hv_mon1 = Column(
    Block('High Voltage Monitors', [
        BlockRow(
            Field(name='monitor Voltage', dev='hv_mon', width=12),
            Field(name='monitor Current', key='hv_mon/current', width=12),
        ),
        BlockRow(
            Field(name='monitor1 Voltage', dev='hv_mon1', width=12),
            Field(name='monitor1 Current', key='hv_mon1/current', width=12),
        ),
        BlockRow(
            Field(name='monitor2 Voltage', dev='hv_mon2', width=12),
            Field(name='monitor2 Current', key='hv_mon2/current', width=12),
        ),
        BlockRow(
            Field(name='monitor3 Voltage', dev='hv_mon3', width=12),
            Field(name='monitor3 Current', key='hv_mon3/current', width=12),
        ),
        BlockRow(
            Field(name='monitor4 Voltage', dev='hv_mon4', width=12),
            Field(name='monitor4 Current', key='hv_mon4/current', width=12),
        ),
        ],
    ),
)

_hv_mon2 = Column(
    Block('High Voltage Detector', [
        BlockRow(
            Field(name='Anode', dev='hv_anode', width=12),
            Field(name='Current', key='hv_anode/current', width=12),
        ),
        BlockRow(
            Field(name='Drift1', dev='hv_drift1', width=12),
            Field(name='Current', key='hv_drift1/current', width=12),
        ),
        BlockRow(
            Field(name='Drift2', dev='hv_drift2', width=12),
            Field(name='Drift2 100%', dev='hv_drift2', width=12),
            Field(name='Current mA', key='hv_drift2/current', width=12),
            Field(name='Current 100%', key='hv_drift2/current', width=12),
        ),
        ],
    ),
)

#Time_selection = [3,'h',60*60]
# Elemente = [
#           #'det_table',
#           #'det_table_acc',
#           #'det_table_analog',
#           'det_table_poti',
#           #'det_table_motor',
#           'det_table_raw',
#           #'det_table_raw.motortemp',
#           #'det_yoke',
#           #'dix_laser_acc',
#           #'dix_laser_analogdix_laser_signalstrength*.1',
#           #'dix_laser_temperature',
#           'dix_laser_value',
#       ]

Time_selection2 = [10,'min',60]
Time_selection1 = [10,'day',24*60*60]
Elemente1 = [
    'det_table',
    'det_table_ctrl',
    'det_table_motor',
    'det_table_poti',
    'det_table_raw',
    'det_yoke',
    'dix_laser_analog',
    #'dix_laser_signalstrength',
    'dix_laser_value',

      ]
Elemente2 = [
    'det_table_cab_temp',
    'det_table_motor_temp',
    'dix_laser_temperature',
    'Temperature2',
    #'det_table_acc',
    #'dix_laser_acc',
      ]

# Time_selection2 = [10,'min',60]
Time_selection10d = [10,'day',24*60*60]
Time_selection10h = [10,'hour', 1*60*60]
Time_selection3h = [3,'h',60*60]

# Elemente1 = [
#     'shutter_gamma_motor',
#     'nok2r_motor',
#     'nok2s_motor',
#     'nok3r_motor',
#     'nok3s_motor',
#     'nok4r_motor',
#     'nok4s_motor',
#     'nok6r_motor',
#     'nok6s_motor',
#     'nok7r_motor',
#     'nok7s_motor',
#     'nok8r_motor',
#     'nok8s_motor',
#     'nok9r_motor',
#     'nok9s_motor',
#     'zb0_motor',
#     'zb1_motor',
#     'zb2_motor',
#     'zb3r_motor',
#     'zb3s_motor',
#     'bs1s_motor',
#     'bs1r_motor',
#     ]
Elemente_acc = [
    'shutter_gamma_acc',
    'nok2r_acc',
    'nok2s_acc',
    'nok3r_acc',
    'nok3s_acc',
    'nok4r_acc',
    'nok4s_acc',
    'nok6r_acc',
    'nok6s_acc',
    'nok7r_acc',
    'nok7s_acc',
    'nok8r_acc',
    'nok8s_acc',
    'nok9r_acc',
    'nok9s_acc',
    'zb2_acc',
    'zb3r_acc',
    'zb3s_acc',
    'bs1s_acc',
    'bs1r_acc',
    ]

wi = 80
he = 45
_plot1_1 = Column(
    Block('History motor %d%s' % (Time_selection1[0], Time_selection1[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  devices=Elemente1,
                  names=Elemente1,
                  legend=True),
        ),
        ],
    ),
)
_plot1_2 = Column(
    Block('History motor %d%s' % (Time_selection2[0], Time_selection2[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection2[0]*Time_selection2[2],
                  devices=Elemente1,
                  names=Elemente1,
                  legend=True),
        ),
        ],
    ),
)
_plot2_1 = Column(
    Block('History acc %d%s' % (Time_selection1[0], Time_selection1[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  devices=Elemente2,
                  names=Elemente2,
                  legend=True),
        ),
        ],
    ),
)
_plot2_2 = Column(
    Block('History acc %d%s' % (Time_selection2[0], Time_selection2[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=wi,
                  height=he,
                  plotwindow=Time_selection2[0]*Time_selection2[2],
                  devices=Elemente2,
                  names=Elemente2,
                  legend=True),
        ),
        ],
    ),
)


Time_selection1 = Time_selection10h
Elemente1 = ['ReactorPower']
Time_selection2 = Time_selection10h
Elemente2 = ['sds']
_plotcolumn = Column(
    Block('Reactor %d%s' % (Time_selection1[0], Time_selection1[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=30,
                  height=15,
                  plotwindow=Time_selection1[0]*Time_selection1[2],
                  devices=Elemente1,
                  names=Elemente1,
                  legend=False),
        ),
        ],
    ),
    Block('SafeDetectorSystem %d%s' % (Time_selection2[0], Time_selection2[1]) , [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=30,
                  height=15,
                  plotwindow=Time_selection2[0]*Time_selection2[2],
                  devices=Elemente2,
                  names=Elemente2,
                  legend=False),
        ),
        ],
    ),
)

one = [
            Row(_shgacol,
                _nok2col,
                _nok3col,
                _nok4col,
                _nok6col,_zb2col,
                ),
            Row(
                _nok7col,_zb3col,
                _nok8col, _bs1col,
                _nok9col,
                ),
            Row(
                _refcolumn,
                _plotcolumn,
                _pumpstand,
                _memograph,
                _05_chopper,
                ),
        ]

vsd = [
            Row(_power, _vsd_chopper, _air),
            Row(_temp),
            Row(_cooling),
        ]

shs = [
        Row(_signal),
        Row(_basis),
        Row(_place),
        Row(_service),
        Row(_supervisor),
        Row(_techOK),
        Row(_personalkey),
        Row(_user),
        ]

plot4x4 = [
        Row(_plot1_1, _plot1_2),
        Row(_plot2_1, _plot2_2),
        ]

hv = [
        Row(_hv_mon1),
        Row(_hv_mon2),
        ]

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = False,
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 11,
        padding = 5,
        layout = one,
        #layout = vsd,
        #layout = shs,
        #layout = plot4x4,
        #layout = hv,
    ),
)
