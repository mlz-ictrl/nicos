description = 'vacuum system monitoring'

group = 'lowlevel'

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    pump_status = device('nicos.devices.tango.DigitalInput',
        description = 'pump status',
        tangodevice = tango_base + 'sps/pump_status',
        fmtstr = '%#02x',
        lowlevel = True,
    ),
    pump_manual_mode = device('nicos.devices.tango.DigitalInput',
        description = 'pump manual mode',
        tangodevice = tango_base + 'sps/pump_manual_mode',
        fmtstr = '%#02x',
        lowlevel = True,
    ),
    pump_request_mode = device('nicos.devices.tango.DigitalInput',
        description = 'pump request mode',
        tangodevice = tango_base + 'sps/pump_request_mode',
        fmtstr = '%#02x',
        lowlevel = True,
    ),
)
