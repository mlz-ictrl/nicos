description = 'Pfeiffer SingleGauge pressure sensor readout'
group = 'optional'

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    p_gauge = device('nicos.devices.entangle.Sensor',
        description = 'SingleGauge sensor',
        tangodevice = tango_base + 'pfeiffergauge/sensor',
        pollinterval = 0.7,
        maxage = 2,
        unit = "mbar",
        fmtstr = "%.6f",
    ),
)

