description = 'Gas Handling PLC'
group = 'lowlevel'

tango_base = 'tango://localhost:10000/dr/panel/'

devices = dict(
    lhe_level = device('nicos.devices.entangle.Sensor',
        description = 'LHe level',
        tangodevice = tango_base + 'lhe',
        pollinterval = 10,
        maxage = 25,
        fmtstr = '%.1f',
        unit = "%",
    ),
)

