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
             Field(name='Phase', dev='chopper_params', unit='deg', item=1)),
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
    BlockRow(Field(name='X', dev='det_x'),
             Field(name='Y', dev='det_y'),
             Field(name='Z', dev='det_z')),
])

_lenses = Block('Lenses', [
    BlockRow(Field(name='Setting', dev='lenses', istext=True, width=17)),
])

_shutter = Block('Shutter', [
    BlockRow(Field(name='Setting', dev='shutter', istext=True, width=10)),
])

_sample = Block('Sample', [
    BlockRow(Field(name='Rotation', dev='sam_rot'),
             Field(name='Trans. 1', dev='sam_trans_1'),
             Field(name='Trans. 2', dev='sam_trans_2')),
    BlockRow(Field(name='Slit', dev='ap_sam', istext=True, width=25)),
])

_daq = Block('Data acquisition', [
    BlockRow(Field(name='Timer', dev='timer'),
             Field(name='Total counts', dev='det_img')),
])

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'KWS-1 status',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'phys.kws1.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Bitstream Vera Sans Mono',
                     padding = 0,
                     layout = [
                         Row(Column(_experiment)),
                         Row(Column(_selector, _chopper, _shutter),
                             Column(_collimation, _polarizer, _lenses),
                             Column(_sample, _detector, _daq)),
                     ],
                    ),
)
