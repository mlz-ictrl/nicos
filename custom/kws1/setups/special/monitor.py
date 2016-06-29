# This setup file configures the nicos status monitor.

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
             Field(name='Last file', key='exp/lastscan')),
])

_selector = Block('Selector', [
    BlockRow(Field(name='Preset', dev='selector', istext=True, width=10)),
    BlockRow(Field(name='Lambda', dev='selector_lambda'),
             Field(name='Speed', dev='selector_speed')),
    BlockRow(Field(name='Vac', dev='selector_vacuum'),
             Field(name='Rotor', dev='selector_rtemp')),
    BlockRow(Field(name='Flow', dev='selector_wflow'),
             Field(name='Vibr', dev='selector_vibrt')),
])

_chopper = Block('Chopper', [
    BlockRow(Field(name='Preset', dev='chopper', istext=True, width=17)),
    BlockRow(Field(name='Frequency', dev='chopper_params', unit='Hz', item=0),
             Field(name='Opening', dev='chopper_params', unit='deg', item=1)),
])

_collimation = Block('Collimation', [
    BlockRow(Field(name='Preset', dev='collimation', istext=True, width=17)),
    BlockRow(Field(name='Guide elements', dev='coll_guides')),
    BlockRow(Field(name='Ap. 20m', dev='aperture_20', istext=True, width=10),
             Field(name='Ap. 14m', dev='aperture_14', istext=True, width=10),
             Field(name='Ap. 8m', dev='aperture_08', istext=True, width=10)),
    BlockRow(Field(name='Ap. 4m', dev='aperture_04', istext=True, width=10),
             Field(name='Ap. 2m', dev='aperture_02', istext=True, width=10)),
])

_polarizer = Block('Polarizer', [
    BlockRow(Field(name='Setting', dev='polarizer', istext=True),
             Field(name='Flipper', dev='flipper', istext=True)),
])

_detector = Block('Detector', [
    BlockRow(Field(name='Preset', dev='detector', istext=True, width=17)),
    BlockRow(
        Field(devices=['det_z', 'det_x', 'det_y'],
              widget='nicos.kws1.monitorwidgets.Tube', width=30, height=10)
    ),
])

_lenses = Block('Lenses', [
    BlockRow(Field(name='Setting', dev='lenses', istext=True, width=17)),
])

_shutter = Block('Shutter', [
    BlockRow(Field(name='Shutter', dev='shutter', istext=True, width=9),
             Field(name='Sixfold', dev='sixfold_shutter', istext=True, width=9)),
])

_sample = Block('Sample', [
    BlockRow(Field(name='Rotation', dev='sam_rot'),
             Field(name='Trans X', dev='sam_trans_x'),
             Field(name='Trans Y', dev='sam_trans_y')),
    BlockRow(Field(name='Slit', dev='ap_sam', istext=True, width=25)),
])

_hexapod = Block('Hexapod', [
    BlockRow(Field(name='TX', dev='hexapod_tx'),
             Field(name='TY', dev='hexapod_ty'),
             Field(name='TZ', dev='hexapod_tz')),
    BlockRow(Field(name='RX', dev='hexapod_rx'),
             Field(name='RY', dev='hexapod_ry'),
             Field(name='RZ', dev='hexapod_rz')),
    BlockRow(Field(name='Table', dev='hexapod_dt')),
], setups='hexapod')

_daq = Block('Data acquisition', [
    BlockRow(Field(name='Timer', dev='timer'),
             Field(name='Total', dev='det_img', item=0, format='%d'),
             Field(name='Rate', dev='det_img', item=1, format='%.1f')),
    BlockRow(Field(name='Mon1', dev='mon1rate'),
             Field(name='Mon2', dev='mon2rate'),
             Field(name='Mon3', dev='mon3rate')),
])

_peltier = Block('Peltier/Julabo', [
    BlockRow('T_peltier', 'T_julabo')
], setups='peltier')

_peltierplot = Block('', [
    BlockRow(Field(plot='TT', dev='T_peltier', width=40, height=25, plotwindow=24*3600),
             Field(plot='TT', dev='T_julabo'),
             Field(plot='TT', key='T_peltier/setpoint'),
             Field(plot='TT', key='T_julabo/setpoint')),
], setups='peltier')

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'KWS-1 status',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'localhost',# 'phys.kws1.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Bitstream Vera Sans Mono',
                     padding = 0,
                     layout = [
                         Row(Column(_experiment)),
                         Row(Column(_selector, _chopper, _shutter, _peltier),
                             Column(_collimation, _polarizer, _lenses, _daq),
                             Column(_sample, _hexapod, _detector, _peltierplot)),
                     ],
                    ),
)
