description = 'Kepco current souces'

group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/'

devices = dict(
    kepco1_current = device('nicos.devices.tango.PowerSupply',
        description = "kepco power supply 1",
        tangodevice = tango_base + 'kepco/current1',
        fmtstr = '%.3f',
    ),
    kepco2_current = device('nicos.devices.tango.PowerSupply',
        description = "kepco power supply 2",
        tangodevice = tango_base + 'kepco/current2',
        fmtstr = '%.3f',
    ),
    kepco3_current = device('nicos.devices.tango.PowerSupply',
        description = "kepco power supply 3",
        tangodevice = tango_base + 'kepco/current3',
        fmtstr = '%.3f',
    ),
    kepco4_current = device('nicos.devices.tango.PowerSupply',
        description = "kepco power supply 4",
        tangodevice = tango_base + 'kepco/current4',
        fmtstr = '%.3f',
    ),
)
