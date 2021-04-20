description = 'Analyzer tower devices'

group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/aircontrol/plc_'

devices = dict(
    # att (A6)
    att_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'att_mot',
        fmtstr = '%.4f',
        lowlevel = True,
    ),
    att_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'att_enc',
        fmtstr = '%.4f',
        lowlevel = True,
    ),
    air_detector = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 'airpads_detector',
        lowlevel = True,
    ),
    att = device('nicos_mlz.mira.devices.axis.HoveringAxis',
        description = 'secondary spectrometer angle (A6)',
        motor = 'att_m',
        coder = 'att_c',
        startdelay = 2,
        stopdelay = 2,
        switch = 'air_detector',
        switchvalues = (0, 1),
        fmtstr = '%.3f',
        precision = 0.001,
    ),
    # apth (S-Bender)
    apth = device('nicos.devices.entangle.Motor',
        description = 'apth',
        tangodevice = tango_base + 'apth_mot',
        fmtstr = '%.4f',
    ),

    # ahfh (Heusler-Analyzer)
    ahfh = device('nicos.devices.entangle.Motor',
        description = 'ahfh',
        tangodevice = tango_base + 'ahfh_mot',
        fmtstr = '%.4f',
    ),
)

for key in ('left', 'right'):
    devices['asb_cyl_' + key] = device('nicos.devices.entangle.NamedDigitalOutput',
        description = '%s ana shielding blocks lifter' % key,
        tangodevice = tango_base + 'asb_cyl_%s' % key,
        mapping = dict(up=1, down=0),
    )
    devices['asb_cyl_%s_ofs' % key] = device('nicos.devices.entangle.AnalogOutput',
        description = 'offset of %s ana shielding blocks lift' % key,
        tangodevice = tango_base + 'asb_cyl_%s_ofs' % key,
        fmtstr = '%.3f',
    )


# ath (A5)
# ac (agx)
# ax (atx)
# ay (aty)
# afh
# afv
for key in ('ath', 'agx', 'atx', 'aty', 'afv', 'afh', ): #'nutator'):
    devices[key] = device('nicos.devices.generic.Axis',
        description = key,
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + '%s_mot' % key,
            fmtstr = '%.4f',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + '%s_enc' % key,
            fmtstr = '%.4f',
        ),
        fmtstr = '%.3f',
        precision = 0.001,
    )

