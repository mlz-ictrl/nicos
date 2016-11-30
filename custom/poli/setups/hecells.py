description = 'Setup for polarization with He cells'

group = 'lowlevel'

includes = ['detector']

sysconfig = dict(
    datasinks = ['hepolsink'],
)

devices = dict(
    hepolsink  = device('poli.he3cell.HePolSink',
                        description = 'Sink that saves monitor ratio for '
                        'polarization calculation',
                        transmission = 'beam_trans',
                        monitors = ('mon1', 'mon2'),
                       ),
    beam_trans = device('poli.he3cell.Transmission',
                        description = 'Monitor2/monitor1 ratio for counts',
                        abslimits = (0, 2),
                        unit = '',
                       ),
    beam_pol   = device('poli.he3cell.BeamPolarization',
                        description = 'Incoming beam polarization calculated '
                        'from beam_trans and He cell parameters',
                        transmission = 'beam_trans',
                        wavelength = 'wavelength',
                       ),
    timestamp  = device('poli.tsdevice.Timestamp',
                        description = 'Timestamp generator for scan env',
                       ),
)
