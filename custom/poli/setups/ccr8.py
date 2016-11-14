description = 'CCR-8 cryo box for controlling compressor'
group = 'optional'

devices = dict(
    ccr8_compressor_switch = device('devices.tango.NamedDigitalOutput',
        description = 'CCR4 compressor switch on/off',
        mapping = {'off': 0, 'on': 1},
        tangodevice = 'tango://phys.poli.frm2:10000/poli/ccr8/pump',
    ),
)
