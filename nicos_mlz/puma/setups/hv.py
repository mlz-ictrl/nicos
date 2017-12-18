description = 'High voltage power supplies'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2:10000/puma/'

devices = dict(
    hvmonitor = device('nicos.devices.tango.PowerSupply',
        description = 'HV for the monitor',
        tangodevice = tango_base + 'monitor/hv',
        fmtstr = '%.0f',
    ),
    hvdetector = device('nicos.devices.tango.PowerSupply',
        description = 'HV for the detectors',
        tangodevice = tango_base + 'detector/hv',
        fmtstr = '%.0f',
    )
)
