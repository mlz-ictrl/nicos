description = '5T SANS Magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = 'tango://ccm5h:10000/box/'

devices = dict(
    B_ccm5h = device('nicos_mlz.devices.ccm5h.AsymmetricMagnet',
        description = 'The resulting magnetic field',
        tangodevice = tango_base + 'magnet/field',
        abslimits = (-5, 5),
        fmtstr = '%.3f',
        maxage = 120,
        pollinterval = 15,
    ),
    I1_ccm5h = device('nicos.devices.entangle.AnalogInput',
        description = 'actual current output of power supply 1',
        tangodevice = tango_base + 'ips1/current',
    ),
    I2_ccm5h = device('nicos.devices.entangle.AnalogInput',
        description = 'actual current output of power supply 2',
        tangodevice = tango_base + 'ips2/current',
    ),

    ccm5h_T_stage1 = device('nicos.devices.entangle.Sensor',
        description = 'Coldhead Stage 1',
        tangodevice = tango_base + 'ips1/t_coldhead_stage1',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_T_stage2 = device('nicos.devices.entangle.Sensor',
        description = 'Coldhead Stage 2',
        tangodevice = tango_base + 'ips1/t_coldhead_stage2',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_T_shield_top = device('nicos.devices.entangle.Sensor',
        description = 'Shield top',
        tangodevice = tango_base + 'ips2/t_shield_top',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_T_shield_bottom = device('nicos.devices.entangle.Sensor',
        description = 'Shield bottom',
        tangodevice = tango_base + 'ips2/t_shield_bottom',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_T_topleft = device('nicos.devices.entangle.Sensor',
        description = 'Coil top left',
        tangodevice = tango_base + 'ips1/t_topleft',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_T_topright = device('nicos.devices.entangle.Sensor',
        description = 'Coil top right',
        tangodevice = tango_base + 'ips1/t_topright',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_T_bottomleft = device('nicos.devices.entangle.Sensor',
        description = 'Coil bottom left (thermometer or wiring broken!)',
        tangodevice = tango_base + 'ips2/t_bottomleft',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_T_bottomright = device('nicos.devices.entangle.Sensor',
        description = 'Coil bottom right',
        tangodevice = tango_base + 'ips2/t_bottomright',
        fmtstr = '%.2f',
        maxage = 120,
        pollinterval = 15,
    ),
    ccm5h_compressor = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Compressor for Coldhead (should be ON)',
        tangodevice = tango_base + 'plc/compressor',
        mapping = {'on': 1, 'off': 0},
    ),
)

alias_config = {
    'B': {'B_ccm5h': 100},
}

extended = dict(
    representative = 'B_ccm5h',
)

monitor_blocks = dict(
    default = Block('SANS-1 5T Magnet', [
        BlockRow(
            Field(name='Field', dev='B_ccm5h', width=12),
        ),
        BlockRow(
            Field(name='Target', key='B_ccm5h/target', width=12),
            Field(name='Asymmetry', key='B_ccm5h/asymmetry', width=12),
        ),
        BlockRow(
            Field(name='Power Supply 1', dev='I1_ccm5h', width=12),
            Field(name='Power Supply 2', dev='I2_ccm5h', width=12),
        ),
    ], setups=setupname),
    temperatures = Block('SANS-1 5T Magnet Temperatures', [
        BlockRow(
            Field(name='CH Stage 1', dev='ccm5h_T_stage1', width=12),
            Field(name='CH Stage 2', dev='ccm5h_T_stage2', width=12),
        ),
        BlockRow(
            Field(name='Shield Top', dev='ccm5h_T_shield_top', width=12),
            Field(name='Shield Bottom', dev='ccm5h_T_shield_bottom', width=12),
        ),
        BlockRow(
            Field(name='Magnet TL', dev='ccm5h_T_topleft', width=12),
            Field(name='Magnet TR', dev='ccm5h_T_topright', width=12),
        ),
        BlockRow(
            Field(name='Magnet BL', dev='ccm5h_T_bottomleft', width=12),
            Field(name='Magnet BR', dev='ccm5h_T_bottomright', width=12),
        ),
    ], setups=setupname),
    plot = Block('SANS-1 5T Magnet plot', [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=40, height=20, plotwindow=1800,
                  devices=['B_ccm5h', 'B_ccm5h/target'],
                  names=['30min', 'Target'],
                  legend=True),
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=40, height=20, plotwindow=12*3600,
                  devices=['B_ccm5h', 'B_ccm5h/target'],
                  names=['12h', 'Target'],
                  legend=True),
        ),
    ], setups=setupname),
)
