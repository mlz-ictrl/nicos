description = 'power supplies'
group = 'optional'

devices = dict()

labels = [
    'solmain1', 'fpi21', 'fpi', 'fpi22', 'solsample_z', 'solpi21', 'solpi21a',
    'solpi22.3', 'solpic1', 'solpic2', '', 'solmain1s', '', '', '', 'cc1r1',
    'loop0yh', 'cc3r1', 'loop0z', 'solphase1', 'solphase2', 'solanalyzer',
    'solpolarizer', 'cc1y1', 'cc1y2', 'cc3y1', 'cc3y2', 'cc1z1', 'cc1z2',
    'cc3z1', 'solphase1s', 'solmain1h', 'solsample1', 'loop1z', 'loop1y',
    'loop2z', 'loop2y', '',
]
for i in range(1, 39):
    devices[f'pow{i:02d}'] = \
        device(
            'nicos_virt_mlz.j_nse.devices.jnse.JNSEVirtualMotor',
            description = f'Power Supply Port {i:02d}',
            label = labels[i - 1],
            userlimits = (-250, 250),
            abslimits = (-250, 250),
            speed = 100.,
            unit = 'A',
            pollinterval = 0.5,
            visibility = ('metadata', 'namespace') if i in [5, 9, 10, 11, 12] \
                else ('metadata', 'namespace', 'devlist'),
        )
