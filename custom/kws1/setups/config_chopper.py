description = 'presets for the chopper/TOF mode'
group = 'configdata'

CHOPPER_PRESETS = {
    ('5A', '2m'): {
        '2.5%': dict(phase=20, freq=72.6238, channels=64, interval=215),
        '5%':   dict(phase=36, freq=65.3614, channels=64, interval=239),
        '10%':  dict(phase=60, freq=54.4679, channels=64, interval=286),
    },
    ('7A', '2m'): {
        '2.5%': dict(phase=20, freq=51.8741, channels=64, interval=301),
        '5%':   dict(phase=36, freq=46.6867, channels=64, interval=334),
        '10%':  dict(phase=60, freq=38.9056, channels=64, interval=401),
    },
}
