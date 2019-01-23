description = 'HGM09 Hand Gauss Meter'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    hgm09 = device('nicos_mlz.antares.devices.hgm09.HGM09',
        description = 'HGM09 Hand Gauss Meter',
        tangodevice = tango_base + 'rs232/hgm09',
    ),
)
