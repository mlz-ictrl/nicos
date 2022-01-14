description = 'Hexapod devices in tool coordinate system'

group = 'lowlevel'

tango_base = 'tango://stressictrl.stressi.frm2.tum.de:10000/stressi/xps_hexapod/'

devices = dict(
    hxpz = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'Z (default work offset = 309)',
        tangodevice = tango_base + 'HXP_Z_Tool',
        precision = 0.001,
    ),
    hxpx = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'X (default work offset = 309)',
        tangodevice = tango_base + 'HXP_X_Tool',
        precision = 0.001,
    ),
    hxpy = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'Y (default work offset = 309)',
        tangodevice = tango_base + 'HXP_Y_Tool',
        precision = 0.001,
    ),
    hxpu = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'U (default work offset = 309)',
        tangodevice = tango_base + 'HXP_U_Tool',
        precision = 0.001,
    ),
    hxpv = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'V (default work offset = 309)',
        tangodevice = tango_base + 'HXP_V_Tool',
        precision = 0.001,
    ),
    hxpw = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'W (default work offset = 309)',
        tangodevice = tango_base + 'HXP_W_Tool',
        precision = 0.001,
    ),
)
