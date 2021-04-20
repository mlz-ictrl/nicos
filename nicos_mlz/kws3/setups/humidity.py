description = 'MHG humidity generator'

group = 'optional'

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = {
    'mhg_flowrate': device('nicos.devices.entangle.WindowTimeoutAO',
        description = 'Flow rate through humidity cell',
        tangodevice = tango_base + 'mhg/flowrate',
        fmtstr = '%.1f',
        unit = 'ml',
        timeout = 600.0,
        precision = 0.2,
    ),
    'mhg_humidity': device('nicos.devices.entangle.WindowTimeoutAO',
        description = 'Humidity in humidity cell',
        tangodevice = tango_base + 'mhg/humidity',
        fmtstr = '%.1f',
        unit = '%',
        timeout = 600.0,
        precision = 1,
    ),
    'T_mhg_cell': device('nicos.devices.entangle.Sensor',
        description = 'Temperature in humidity cell',
        tangodevice = tango_base + 'mhg/temperature',
        fmtstr = '%.1f',
        unit = 'degC',
    ),
}
