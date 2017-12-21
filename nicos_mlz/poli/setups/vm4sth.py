description = 'setup for VM4 magnet'

group = 'optional'
includes = ['alias_sth', 'vm4']

DELTA = 0.

devices = dict(
    sth_vm4_om = device('nicos_mlz.poli.devices.magnet.MagnetSampleTheta',
        description = 'sample theta angle combining sample and magnet rotation',
        sample_theta = 'sth_vm4',
        magnet_theta = 'omega',
        two_theta = 'gamma',
        unit = 'deg',
        fmtstr = '%.3f',
        blocked = [
            (DELTA + 55, DELTA + 110),
            (DELTA + 185, DELTA + 240),
            (DELTA + 305, DELTA + 360)
        ],
    ),
)

alias_config = {
    'sth': {'sth_vm4_om': 200},
}
