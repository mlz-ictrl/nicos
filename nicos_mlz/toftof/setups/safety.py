description = 'safety system and shutter'

group = 'lowlevel'

includes = []

tango_host = 'tango://tofhw.toftof.frm2:10000/toftof/'

devices = dict(
    saf = device('nicos_mlz.toftof.devices.safety.SafetyInputs',
        description = 'State of the safety control',
        i7053 = ['i7053_1', 'i7053_2', 'i7053_3'],
        fmtstr = '0x%012x',
    ),
    i7053_1 = device('nicos.devices.tango.DigitalInput',
        lowlevel = True,
        tangodevice = tango_host + 'sec/70531',
        fmtstr = '0x%04x',
    ),
    i7053_2 = device('nicos.devices.tango.DigitalInput',
        lowlevel = True,
        tangodevice = tango_host + 'sec/70532',
        fmtstr = '0x%04x',
    ),
    i7053_3 = device('nicos.devices.tango.DigitalInput',
        lowlevel = True,
        tangodevice = tango_host + 'sec/70533',
        fmtstr = '0x%04x',
    ),
    shopen = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_host + 'shutter/open',
        lowlevel = True,
    ),
    shclose = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_host + 'shutter/close',
        lowlevel = True,
    ),
    shstatus = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_host + 'shutter/status',
        lowlevel = True,
    ),
    shutter = device('nicos_mlz.toftof.devices.safety.Shutter',
        description = 'Instrument shutter',
        open = 'shopen',
        close = 'shclose',
        status = 'shstatus',
        unit = '',
    ),
)
