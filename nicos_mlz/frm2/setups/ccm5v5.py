description = 'FRM II 5.5 T superconducting magnet'

group = 'plugplay'

includes = ['alias_B', 'alias_sth']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'B_{setupname}': device('nicos.devices.entangle.Actuator',
        description = 'The magnetic field',
        tangodevice = tango_base + 'magnet/field',
        abslimits = (-5.555, 5.555),
    ),
    f'sth_{setupname}': device('nicos.devices.generic.Axis',
        description = 'Cryotstat tube rotation',
        abslimits = (-180, 180),
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'motor/motor',
            visibility = (),
            ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'motor/encoder',
            visibility = (),
            ),
        precision = 0.001,
    ),
}

# Maximum temeratures for field operation above 80A taken from the manual
maxtemps = [None, 4.3, 4.3, 5.1, 4.7, None, None, None, 4.3]

for i in range(1, 9):
    dev = device('nicos.devices.entangle.Sensor',
        description = '5.5T magnet temperature sensor %d' % i,
        tangodevice = tango_base + 'lakeshore/sensor%d' % i,
        warnlimits = (0, maxtemps[i]),
        pollinterval = 30,
        maxage = 90,
        unit = 'K',
    )
    devices['%s_T%d' % (setupname, i)] = dev

alias_config = {
    'B':   {f'B_{setupname}': 100},
    'sth': {f'sth_{setupname}': 100},
}

extended = dict(
    representative = f'B_{setupname}',
)

monitor_blocks = dict(
    default = Block('5T Magnet', [
        BlockRow(
            Field(dev='B_ccm5v5', name='Field', fmtstr='%.3f'),
            Field(key='B_ccm5v5/target', name='Target', fmtstr='%.2f'),
            Field(dev='sth_ccm5v5', name='sth'),
        ),
    ], setups='ccm5v5'),
    temperatures = Block('5T Magnet', [
        # Maximum temperatures for field operation above 6.6 T (80A)
        # taken from the manual
        BlockRow(
            Field(dev='ccm5v5_T1', max=4.3),
            Field(dev='ccm5v5_T2', max=4.3),
        ),
        BlockRow(
            Field(dev='ccm5v5_T3', max=5.1),
            Field(dev='ccm5v5_T4', max=4.7),
        ),
        BlockRow(
            Field(dev='ccm5v5_T5'),
            Field(dev='ccm5v5_T6'),
        ),
        BlockRow(
            Field(dev='ccm5v5_T7'),
            Field(dev='ccm5v5_T8', max=4.3),
        ),
    ], setups='ccm5v5'),
    plots = Block('5T Magnet plots', [
        BlockRow(
            Field(dev='ccm5v5_T1', name='T1', plot='Tm', plotwindow=24*3600,
                  width=100, height=40),
            Field(dev='ccm5v5_T2', name='T2', plot='Tm'),
            Field(dev='ccm5v5_T3', name='T3', plot='Tm'),
            Field(dev='ccm5v5_T4', name='T4', plot='Tm'),
            Field(dev='B', plot='Tm'),
        ),
    ], setups='ccm5v5'),
)
