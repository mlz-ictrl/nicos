description = 'power supplies'
group = 'optional'

devices = dict()

for i in range(1, 39):
    devices[f'pow{i:02d}'] = \
        device(
            'nicos_virt_mlz.j_nse.devices.jnse.JNSEVirtualMotor',
            description = f'Power Supply Port {i:02d}',
            userlimits = (-250, 250),
            abslimits = (-250, 250),
            speed = 100.,
            unit = 'A',
            pollinterval = 0.5,
            visibility = ('metadata', 'namespace') if i in [5, 9, 10, 11, 12] \
                else ('metadata', 'namespace', 'devlist'),
        )
