description = 'Hexapod devices in work coordinate system'

group = 'lowlevel'

tango_base = 'tango://stressictrl.stressi.frm2.tum.de:10000/stressi/xps_hexapod/'

devices = dict(
    hxpz_w = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'Z (default work offset = 309)',
        tangodevice = tango_base + 'HXP_Z_Work',
        precision = 0.001,
        visibility = (),
    ),
    hxpx_w = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'X (default work offset = 309)',
        tangodevice = tango_base + 'HXP_X_Work',
        precision = 0.001,
        visibility = (),
    ),
    hxpy_w = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'Y (default work offset = 309)',
        tangodevice = tango_base + 'HXP_Y_Work',
        precision = 0.001,
        visibility = (),
    ),
    hxpu_w = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'U (default work offset = 309)',
        tangodevice = tango_base + 'HXP_U_Work',
        precision = 0.001,
        visibility = (),
    ),
    hxpv_w = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'V (default work offset = 309)',
        tangodevice = tango_base + 'HXP_V_Work',
        precision = 0.001,
        visibility = (),
    ),
    hxpw_w = device('nicos_mlz.devices.newport.HexapodAxis',
        description = 'W (default work offset = 309)',
        tangodevice = tango_base + 'HXP_W_Work',
        precision = 0.001,
        visibility = (),
    ),
)
