description = 'SmarAct stick-slip piezo motor slit'

# TODO: opmode, coordinates, lowlevel

group = 'optional'

tango_base = 'tango://phys.maria.frm2:10000/maria/'
piezo_slit = tango_base + 'smaract/piezo_'

devices = dict(
    piezo_left = device('nicos.devices.entangle.Motor',
        description = 'Left blade of the SmarAct piezo slit',
        tangodevice = piezo_slit + 'left',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
        lowlevel = False,
    ),
    piezo_right = device('nicos.devices.entangle.Motor',
        description = 'Right blade of the SmarAct piezo slit',
        tangodevice = piezo_slit + 'right',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
        lowlevel = False,
    ),
    piezo_bottom = device('nicos.devices.entangle.Motor',
        description = 'Bottom blade of the SmarAct piezo slit',
        tangodevice = piezo_slit + 'bottom',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
        lowlevel = False,
    ),
    piezo_top = device('nicos.devices.entangle.Motor',
        description = 'Top blade of the SmarAct piezo slit',
        tangodevice = piezo_slit + 'top',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
        lowlevel = False,
    ),
    piezo_slit = device('nicos.devices.generic.Slit',
        description = 'SmarAct piezo slit',
        left = 'piezo_left',
        right = 'piezo_right',
        bottom = 'piezo_bottom',
        top = 'piezo_top',
        opmode = 'offcentered',
        coordinates = 'opposite',
    ),
)

extended = dict(
    representative = 'piezo_slit',
)
