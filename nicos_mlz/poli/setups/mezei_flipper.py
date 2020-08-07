description = 'Cryopad current settings'

group = 'optional'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    mezeiflipcur = device('nicos.devices.tango.PowerSupply',
        description = 'Flipper Mezei flipper current',
        tangodevice = tango_base + 'delta/cur7',
        fmtstr = '%.2f',
        abslimits = (0, 5),
        unit = 'A',
        pollinterval = 60,
        maxage = 65,
    ),
    mezeicompcur = device('nicos.devices.tango.PowerSupply',
        description = 'Flipper Mezei compensation current',
        tangodevice = tango_base + 'delta/cur8',
        fmtstr = '%.2f',
        abslimits = (0, 5),
        unit = 'A',
        pollinterval = 60,
        maxage = 65,
    ),
    mezeiflipper = device('nicos.devices.polarized.MezeiFlipper',
        description = 'Mezei flipper using mezeiflipcur and mezeicompcur supplies',
        flip = 'mezeiflipcur',
        corr = 'mezeicompcur',
    ),

)
