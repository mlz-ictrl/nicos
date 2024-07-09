description = 'PG Analyzer focus devices'

group = 'lowlevel'
excludes = ['ana_heusler']

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/aircontrol/plc_'

devices = dict(
    afh = device('nicos.devices.generic.Axis',
        description = 'horizontal focus of pg ana',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'afh_mot',
            fmtstr = '%.4f',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'afh_enc',
            fmtstr = '%.4f',
        ),
        fmtstr = '%.3f',
        precision = 0.001,
    ),
    afv = device('nicos.devices.generic.Axis',
        description = 'vertical focus of pg ana',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'afv_mot',
            fmtstr = '%.4f',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'afv_enc',
            fmtstr = '%.4f',
        ),
        fmtstr = '%.3f',
        precision = 0.001,
    ),
)

startupcode = '''
'''
