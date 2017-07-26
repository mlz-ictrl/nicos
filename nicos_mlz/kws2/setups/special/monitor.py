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
             Field(name='Last file', key='exp/lastpoint')),
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
    BlockRow(Field(name='Frequency', dev='chopper_params[0]', unit='Hz'),
             Field(name='Opening', dev='chopper_params[1]', unit='deg')),
])

_collimation = Block('Collimation', [
    BlockRow(Field(name='Preset', dev='collimation', istext=True, width=17)),
    BlockRow(Field(devices=['coll_in', 'coll_out', 'aperture_20', 'aperture_14',
                            'aperture_08', 'aperture_04', 'aperture_02',
                            'pol_in', 'pol_out'],
                   polarizer=2,
                   widget='nicos_mlz.kws1.gui.monitorwidgets.Collimation',
                   width=70, height=12)),
])

_detector = Block('Detector', [
    BlockRow(Field(name='Preset', dev='detector', istext=True, width=17),
             Field(name='GE HV', dev='gedet_HV', istext=True)),
    BlockRow(
        Field(devices=['det_z', 'beamstop_x', 'beamstop_y', 'psd_x', 'psd_y'],
              smalldet=16.0, beamstop=True,
              widget='nicos_mlz.kws1.gui.monitorwidgets.Tube', width=70, height=12)
    ),
])

_polarizer = Block('Polarizer/Lenses', [
    BlockRow(Field(name='Pol. setting', dev='polarizer', istext=True),
             Field(name='Flipper', dev='flipper', istext=True)),
    BlockRow(
        Field(devices=['lens_in', 'lens_out'],
              widget='nicos_mlz.kws1.gui.monitorwidgets.Lenses', width=30, height=10)
    ),
])

_shutter = Block('Shutter', [
    BlockRow(Field(name='Shutter', dev='shutter', istext=True, width=9),
             Field(name='Sixfold', dev='sixfold_shutter', istext=True, width=9)),
])

_sample = Block('Sample', [
    BlockRow(Field(name='Trans X', dev='sam_trans_x'),
             Field(name='Trans Y', dev='sam_trans_y'),
             Field(device='ap_sam', widget='nicos_mlz.kws1.gui.monitorwidgets.SampleSlit',
                   width=10, height=10),
            ),
], setups='not sample_rotation')

_sample_withrot = Block('Sample', [
    BlockRow(Field(name='Rotation', dev='sam_rot'),
             Field(name='Tilt', dev='sam_tilt'),
             Field(name='Trans X', dev='sam_trans_x'),
             Field(name='Trans Y', dev='sam_trans_y'),
             Field(device='ap_sam', widget='nicos_mlz.kws1.gui.monitorwidgets.SampleSlit',
                   width=10, height=10),
            ),
], setups='sample_rotation')

_daq = Block('Data acquisition', [
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
    BlockRow(Field(plot='TT', dev='T_peltier', width=40, height=25, plotwindow=2*3600),
             Field(plot='TT', dev='T_julabo'),
             Field(plot='TT', key='T_peltier/setpoint'),
             Field(plot='TT', key='T_julabo/setpoint')),
], setups='peltier')

_julabo = Block('Julabo', [
    BlockRow('T_julabo')
], setups='waterjulabo and not peltier')

_julaboplot = Block('', [
    BlockRow(Field(plot='JT', dev='T_julabo', width=40, height=25, plotwindow=2*3600),
             Field(plot='JT', key='T_julabo/setpoint')),
], setups='waterjulabo and not peltier')

_et = Block('Eurotherm', [
    BlockRow('T_et')
], setups='eurotherm')

_etplot = Block('', [
    BlockRow(Field(plot='ET', dev='T_et', width=40, height=25, plotwindow=2*3600),
             Field(plot='ET', key='T_et/setpoint')),
], setups='eurotherm')


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = 'KWS-2 status',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'phys.kws2.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Bitstream Vera Sans Mono',
                     padding = 0,
                     layout = [
                         Row(Column(_experiment)),
                         Row(Column(_selector, _chopper, _polarizer, _daq),
                             Column(_shutter, _collimation, _detector, _sample, _sample_withrot),
                             Column(_peltier, _peltierplot, _et, _etplot, _julabo, _julaboplot)),
                     ],
                    ),
)
