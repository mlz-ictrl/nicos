description = 'FRM II FAK40 information (cooling water system)'

group = 'lowlevel'
tango_base = 'tango://ictrlfs.ictrl.frm2:10000/frm2/'


devices = dict(
    FAK40_Cap = device('nicos.devices.entangle.AnalogInput',
        tangodevice = tango_base +'fak40/CF001',
        description = 'The capacity of the cooling water system',
        pollinterval = 60,
        maxage = 120,
    ),
    FAK40_Press = device('nicos.devices.entangle.AnalogInput',
        tangodevice = tango_base +'fak40/CP001',
        description = 'The pressure inside the cooling water system',
        pollinterval = 60,
        maxage = 120,
    ),
)
