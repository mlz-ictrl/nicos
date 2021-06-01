description = 'setup for the status monitor'
group = 'special'

_experiment = Block('Experiment', [
    BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
             Field(name='Title',    key='exp/title',    width=20,
                   istext=True, maxlen=20),
             Field(name='Sample',   key='sample/samplename', width=15,
                   istext=True, maxlen=15),
             Field(name='Current status', key='exp/action', width=40,
                   istext=True, maxlen=40),
             Field(name='Last file', key='exp/lastpoint')),
])

def make_blocks(name, setup, rows, setups=None):
    import copy
    if setups:
        postfix = ' and (' + setups + ')'
    else:
        postfix = ''
    return [
        Block(name, rows, setups=setup + postfix),
        Block('VIRTUAL ' + name, copy.deepcopy(rows), setups='virtual_' + setup + postfix),
    ]

_selector = make_blocks('Selector', 'selector', [
    BlockRow(Field(name='Preset', dev='selector', istext=True, width=10)),
    BlockRow(Field(name='Lambda', dev='selector_lambda'),
             Field(name='Speed', dev='selector_speed')),
    BlockRow(Field(name='Vac', dev='selector_vacuum'),
             Field(name='Rotor', dev='selector_rtemp')),
    BlockRow(Field(name='Flow', dev='selector_wflow'),
             Field(name='Vibr', dev='selector_vibrt')),
])

_chopper = make_blocks('Chopper', 'chopper', [
    BlockRow(Field(name='Preset', dev='chopper', istext=True, width=17)),
    BlockRow(Field(name='Frequency', dev='chopper_params[0]', unit='Hz'),
             Field(name='Opening', dev='chopper_params[1]', unit='deg')),
])

_collimation = make_blocks('Collimation', 'collimation', [
    BlockRow(Field(name='Preset', dev='collimation', istext=True, width=17)),
    BlockRow(Field(devices=['coll_in', 'coll_out', 'aperture_20', 'aperture_14',
                            'aperture_08', 'aperture_04', 'aperture_02'],
                   widget='nicos_mlz.kws1.gui.monitorwidgets.Collimation',
                   width=70, height=13)),
])

_detector = make_blocks('Detector', 'detector', [
    BlockRow(Field(name='Preset', dev='detector', istext=True, width=17),
             Field(name='GE HV', dev='gedet_HV', istext=True)),
    BlockRow(
        Field(devices=['det_z', 'beamstop_x', 'beamstop_y'],
              beamstop=True,
              widget='nicos_mlz.kws1.gui.monitorwidgets.Tube', width=70, height=13)
    ),
])

_polarizer = make_blocks('Polarizer', 'polarizer', [
    BlockRow(Field(name='Pol. setting', dev='polarizer', istext=True),
             Field(name='Flipper', dev='flipper', istext=True)),
])

_lenses = make_blocks('Lenses', 'lenses', [
    BlockRow(
        Field(devices=['lens_in', 'lens_out'],
              widget='nicos_mlz.kws1.gui.monitorwidgets.Lenses', width=30, height=8)
    ),
])

_shutter = make_blocks('Shutter / Outside', 'shutter', [
    BlockRow(Field(name='Shutter', dev='shutter', istext=True, width=9),
             Field(name='NL-3b', dev='nl3b_shutter', istext=True, width=9),
             Field(name='Sixfold', dev='sixfold_shutter', istext=True, width=9),
             Field(name='U-Bahn', dev='UBahn', istext=True, width=12),
             Field(name='Temp', dev='OutsideTemp')),
])

_sample = make_blocks('Sample', 'sample', [
    BlockRow(Field(name='Trans X', dev='sam_trans_x'),
             Field(name='Trans Y', dev='sam_trans_y'),
             Field(device='ap_sam', widget='nicos_mlz.kws1.gui.monitorwidgets.SampleSlit',
                   width=10, height=10)),
], setups='not sample_rotation')

_sample_withrot = make_blocks('Sample', 'sample', [
    BlockRow(Field(name='Rotation', dev='sam_rot'),
             Field(name='Trans X', dev='sam_trans_x'),
             Field(name='Trans Y', dev='sam_trans_y'),
             Field(device='ap_sam', widget='nicos_mlz.kws1.gui.monitorwidgets.SampleSlit',
                   width=10, height=10)),
], setups='sample_rotation')

_hexapod = Block('Hexapod', [
    BlockRow(Field(name='TX', dev='hexapod_tx'),
             Field(name='TY', dev='hexapod_ty'),
             Field(name='TZ', dev='hexapod_tz')),
    BlockRow(Field(name='RX', dev='hexapod_rx'),
             Field(name='RY', dev='hexapod_ry'),
             Field(name='RZ', dev='hexapod_rz')),
    BlockRow(Field(name='Table', dev='hexapod_dt')),
], setups='hexapod')

_daq = make_blocks('Data acquisition', 'daq', [
    BlockRow(Field(name='Timer', dev='timer'),
             Field(name='Total', dev='det_img[0]', format='%d'),
             Field(name='Rate', dev='det_img[1]', format='%.1f')),
    BlockRow(Field(name='Mon1', dev='mon1rate'),
             Field(name='Mon2', dev='mon2rate'),
             Field(name='Mon3', dev='mon3rate')),
])

_peltier = Block('Peltier/Julabo', [
    BlockRow('T_peltier', 'T_julabo')
], setups='peltier')

_peltierplot = Block('', [
    BlockRow(Field(plot='TT', dev='T_peltier', width=30, height=25, plotwindow=2*3600),
             Field(plot='TT', key='T_peltier/setpoint'),
             Field(plot='TT', dev='T_julabo'),
             Field(plot='TT', key='T_julabo/setpoint')),
], setups='peltier')

_julabo = Block('Julabo', [
    BlockRow('T_julabo')
], setups='waterjulabo and not peltier')

_julaboplot = Block('', [
    BlockRow(Field(plot='JT', dev='T_julabo', width=30, height=25, plotwindow=2*3600),
             Field(plot='JT', key='T_julabo/setpoint')),
], setups='waterjulabo and not peltier')

_et = Block('Eurotherm', [
    BlockRow('T_et')
], setups='eurotherm')

_etplot = Block('', [
    BlockRow(Field(plot='ET', dev='T_et', width=30, height=25, plotwindow=2*3600),
             Field(plot='ET', key='T_et/setpoint')),
], setups='eurotherm')

_ccr = Block('Cryostat (CCR11)', [
    BlockRow(Field(name='Setpoint', key='t/setpoint', unitkey='t/unit', format='%.2f'),
             Field(name='Tube', dev='T'), Field(dev='Ts', name='Sample')),
    BlockRow(Field(name='P', key='t/p'), Field(name='I', key='t/i'),
             Field(name='D', key='t/d'), Field(name='p', dev='ccr11_p2')),
    ],
    setups='ccr11',
)

_ccrplot = Block('', [
    BlockRow(Field(plot='CCR', dev='T', width=30, height=25, plotwindow=2*3600),
             Field(plot='CCR', key='T/setpoint'),
             Field(plot='CCR', key='Ts')),
], setups='ccr11')

_ccm3a = Block('HTS Magnet (ccm3a)', [
    BlockRow(Field(name='Field', dev='b_ccm3a')),
    BlockRow(Field(name='T1', dev='ccm3a_t1'), Field(name='T2', dev='ccm3a_t2'),
             Field(name='TA', dev='ccm3a_ta'), Field(name='TB', dev='ccm3a_tb')),
    ],
    setups='ccm3a',
)

_ccm3aplot = Block('', [
    BlockRow(Field(plot='CCM3a', dev='ccm3a_t1', width=30, height=25, plotwindow=2*3600),
             Field(plot='CCM3a', dev='ccm3a_t2'),
             Field(plot='CCM3a', dev='ccm3a_ta'), Field(plot='CCM3a', dev='ccm3a_tb')),
], setups='ccm3a')


_magnet = Block('Electromagnet', [
    BlockRow(Field(name='Current', dev='I_em1')),
], setups='em1')

_layout = [
    Row(Column(_experiment)),
    Row(Column(*(_selector + _chopper + _polarizer + _lenses + _daq)),
        Column(*(_shutter + _collimation + _detector + _sample + _sample_withrot)),
        Column(_hexapod, _peltier, _peltierplot, _et, _etplot,
               _julabo, _julaboplot, _ccr, _ccrplot, _magnet, _ccm3a, _ccm3aplot)),
]


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'KWS-1 status',
        loglevel = 'info',
        cache = 'localhost',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 14,
        padding = 3,
        layout = _layout,
    ),
)
