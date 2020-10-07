description = '3He insert from FRM II Sample environment group'

group = 'plugplay'

includes = ['alias_T']

plc_tango_base = 'tango://%s:10000/box/plc/_' % setupname
ls_tango_base = 'tango://%s:10000/box/lakeshore/' % setupname


devices = {
    'T_%s' % setupname: device('nicos.devices.tango.TemperatureController',
        description = 'The control device to the 3He pot',
        tangodevice = ls_tango_base + 'control',
        abslimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    'T_%s_A' % setupname: device('nicos.devices.tango.Sensor',
        description = 'The mixing chamber temperature',
        tangodevice = ls_tango_base + 'sensora',
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    'T_%s_B' % setupname: device('nicos.devices.tango.Sensor',
        description = 'The sample temperature (if installed)',
        tangodevice = ls_tango_base + 'sensorb',
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    '%s_p_still' % setupname: device('nicos.devices.tango.AnalogInput',
        description = 'Pressure turbo pump inlet = still pressure',
        tangodevice = plc_tango_base + 'pStill',
        fmtstr = '%.3e',
    ),
    '%s_p_inlet' % setupname: device('nicos.devices.tango.AnalogInput',
        description = 'Pressure turbo pump outlet = prePump inlet',
        tangodevice = plc_tango_base + 'pInlet',
        fmtstr = '%.3g',
    ),
    '%s_p_outlet' % setupname: device('nicos.devices.tango.AnalogInput',
        description = 'Pressure compressor inlet = prePump outlet',
        tangodevice = plc_tango_base + 'pOutlet',
        fmtstr = '%.3g',
    ),
    '%s_p_cond' % setupname: device('nicos.devices.tango.AnalogInput',
        description = 'Pressure compressor outlet = condensing pressure',
        tangodevice = plc_tango_base + 'pKond',
        fmtstr = '%.3g',
    ),
    '%s_p_dump' % setupname: device('nicos.devices.tango.AnalogInput',
        description = 'Pressure in dump',
        tangodevice = plc_tango_base+ 'pTank',
        fmtstr = '%.3g',
    ),
    '%s_p_vac' % setupname: device('nicos.devices.tango.AnalogInput',
        description = 'Pressure vacuum dewar',
        tangodevice = plc_tango_base + 'pVacc',
        fmtstr = '%.2e',
    ),
    '%s_p_v15' % setupname: device('nicos.devices.tango.AnalogInput',
        description = 'Pressure on pumping side of V15',
        tangodevice = plc_tango_base + 'pV15',
        fmtstr = '%.2e',
    ),
}

alias_config = {
    'T':  {'T_%s' % setupname: 300},
    'Ts': {'T_%s_A' % setupname: 300, 'T_%s_B' % setupname: 280},
}

extended = dict(
    representative = 'T_%s' % setupname,
)
