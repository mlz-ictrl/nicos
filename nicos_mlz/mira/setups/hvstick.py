description = 'high voltage stick'

tango_base = 'tango://miractrl.mira.frm2:10000/mira/'

devices = dict(
    HV = device('nicos.devices.entangle.PowerSupply',
        description = 'voltage on the HV stick',
        tangodevice = tango_base + 'fughv/voltage',
        abslimits = (-5000, 5000),
    ),
)
