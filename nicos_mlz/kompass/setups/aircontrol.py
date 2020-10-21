description = 'Aircontrol PLC devices'

group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/aircontrol/'

devices = dict(
    ahfh = device('nicos.devices.tango.Motor',
            tangodevice = tango_base + 'plc_ahfh_mot',
            description = "Heusler-ANA horizontal focus",
            fmtstr = '%.4f',
    ),
)
for key in ('att', 'ath', 'agx', 'atx', 'aty', 'apth', 'afv', 'afh', ): #'nutator'):
    devices[key] = device('nicos.devices.generic.Axis',
        description = key,
        motor = device('nicos.devices.tango.Motor',
            tangodevice = tango_base + 'plc_%s_mot' % key,
            fmtstr = '%.4f',
        ),
        coder = device('nicos.devices.tango.Sensor',
            tangodevice = tango_base + 'plc_%s_enc' % key,
            fmtstr = '%.4f',
        ),
        fmtstr = '%.3f',
        precision = 0.001,
    )
