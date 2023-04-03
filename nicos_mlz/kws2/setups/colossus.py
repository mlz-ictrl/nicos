description = 'COLOSSUS sample wheel and temperature control'

group = 'optional'

includes = ['alias_T']

tango_main = 'tango://phys.kws2.frm2:10000/kws2/'
tango_box = 'tango://colossus.kws2.frm2:10000/box/'

wheel_positions = {}
section_offsets = [0, 60, 120, 180, 240, 300]
for (i, off) in enumerate(section_offsets):
    for j in range(8):
        wheel_positions[str(i*8 + j + 1)] = off + j*7.25

devices = dict(
    colossus = device('nicos.devices.entangle.Motor',
        description = 'Colossus wheel position',
        tangodevice = tango_main + 'fzjs7/colossus',
        unit = 'deg',
        precision = 0.01,
    ),
    colossus_sample = device('nicos.devices.generic.Switcher',
        description = 'Colossus sample position',
        moveable = 'colossus',
        mapping = wheel_positions,
        precision = 0.01,
    ),
)

for n in range(1, 7):
    devices[f'T_colossus_{n}'] = device('nicos.devices.entangle.TemperatureController',
        description = f'Temperature controller for section {n}',
        tangodevice = tango_box + f'tc{n}/control',
        abslimits = (5, 140),
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 1800.0,
    )

alias_config = {
    'T':  {'T_colossus_1': 100},
    'Ts': {'T_colossus_1': 100},
}

extended = dict(
    representative = 'colossus',
)
