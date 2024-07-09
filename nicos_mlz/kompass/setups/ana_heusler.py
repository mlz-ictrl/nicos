description = 'Heusler analyzer focus device'

group = 'lowlevel'
excludes = ['ana_pg']

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/aircontrol/plc_'

devices = dict(
    # ahfh (Heusler-Analyzer)
    ahfh = device('nicos.devices.entangle.Motor',
        description = 'Horizontal focus of Heusler ana.',
        tangodevice = tango_base + 'ahfh_mot',
        fmtstr = '%.4f',
    ),
)

startupcode = '''
enable(ahfh)
'''

