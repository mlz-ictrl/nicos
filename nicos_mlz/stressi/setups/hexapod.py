description = 'hexapod playground'

tango_base = 'tango://stressictrl.stressi.frm2.tum.de:10000/stressi/xps_hexapod/'

includes = ['hexapod_tool', 'hexapod_work']

devices = dict(
    hxpm = device('nicos_mlz.devices.newport.HexapodMaster',
        description = 'Hexapod master',
        tangodevice = tango_base + 'master',
    ),
)
