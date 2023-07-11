description = 'MIRA 0.5 T electromagnet'
group = 'plugplay'

includes = ['alias_B']

tango_base = f'tango://{setupname}:10000/box/'

devices = dict(
    I_miramagnet = device('nicos.devices.entangle.RampActuator',
        description = 'MIRA Helmholtz magnet current',
        tangodevice = tango_base + 'plc/_i',
        abslimits = (-250, 250),
        fmtstr = '%.1f',
        unit = 'A',
    ),
    B_miramagnet = device('nicos.devices.generic.CalibratedMagnet',
        currentsource = 'I_miramagnet',
        description = 'MIRA magnetic field',
        # no abslimits: they are automatically determined from I
        unit = 'T',
        fmtstr = '%.4f',
    ),
    miramagnet_pol = device('nicos.devices.entangle.DigitalInput',
        description = 'Polarity of magnet current',
        tangodevice = tango_base + 'plc/_polarity',
        fmtstr = '%+d',
    ),
)

for i in range(1, 5):
    dev = device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature %d of the miramagnet coils' % i,
        tangodevice = tango_base + 'plc/_t%d' % i,
        fmtstr = '%d',
        warnlimits = (0, 60),
        unit = 'degC',
    )
    devices['%s_T%d' % (setupname, i)] = dev

alias_config = {
    # I is included for the rare case you would need to use the current directly
    'B': {'B_miramagnet': 100, 'I_miramagnet': 80},
}

extended = dict(
    representative = 'B_miramagnet',
)

monitor_blocks = dict(
    default = Block('MIRA 0.5T Magnet', [
        BlockRow(
            Field(name='Field', dev='B_miramagnet', width=12),
            Field(name='Target', key='B_miramagnet/target', width=12),
        ),
        BlockRow(
            Field(name='Current', dev='I_miramagnet', width=12),
        ),
    ], setups=setupname),
    temperatures = Block('MIRA 0.5T Magnet temperatures', [
        BlockRow(
            Field(name='T1', dev='miramagnet_T1', width=6, format='%d'),
            Field(name='T2', dev='miramagnet_T2', width=6, format='%d'),
        ),
        BlockRow(
            Field(name='T3', dev='miramagnet_T3', width=6, format='%d'),
            Field(name='T4', dev='miramagnet_T4', width=6, format='%d'),
        ),
    ], setups=setupname),
    plot = Block('MIRA 0.5T Magnet plot', [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=60, height=15, plotwindow=1800,
                  devices=['B_miramagnet', 'B_miramagnet/target'],
                  names=['30min', 'Target'],
                  legend=True),
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=60, height=15, plotwindow=24*3600,
                  devices=['B_miramagnet', 'B_miramagnet/target'],
                  names=['24h', 'Target'],
                  legend=True),
        ),
    ], setups=setupname),
)
