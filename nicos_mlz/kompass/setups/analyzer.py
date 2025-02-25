description = 'Analyzer tower devices'

group = 'lowlevel'

tango_base = 'tango://kompasshw.kompass.frm2.tum.de:10000/kompass/aircontrol/plc_'

devices = dict(
    # att (A6)
    att_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'att_mot',
        fmtstr = '%.4f',
        visibility = (),
    ),
    att_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'att_enc',
        fmtstr = '%.4f',
        visibility = (),
    ),
    air_detector = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 'airpads_detector',
        visibility = (),
    ),
    att = device('nicos_mlz.devices.axes.HoveringAxis',
        description = 'secondary spectrometer angle (A6)',
        motor = 'att_m',
        coder = 'att_c',
        abslimits = (-130, 130),
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

    ana = device('nicos.devices.tas.Monochromator',
        description = 'Analyzer unit to move outgoing wavevector',
        unit = 'A-1',
        material = 'PG',
        reflection = (0, 0, 2),
        dvalue = 3.355,
        theta = 'ath',
        twotheta = 'att',
        focush = None,
        focusv = None,
        abslimits = (0.1, 10),
        scatteringsense = 1,
        crystalside = 1,
    ),
)

# ath (A5)
# ac (agx)
# ax (atx)
# ay (aty)
for key in ('ath', 'agx', 'atx', 'aty', ):  #'nutator'):
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

startupcode = '''
att.motor.speed=0.4
'''
