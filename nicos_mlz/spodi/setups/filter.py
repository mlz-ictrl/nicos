description = 'Graphite filter devices'

group = 'lowlevel'

tango_base = 'tango://%s:10000/spodi/filterbox/' % 'spodictrl.spodi.frm2'

devices = dict(
    filter = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Graphite filter device',
        tangodevice = tango_base + 'filter_filterinout',
        mapping = {'in': 1,
                   'out': 0},
    ),
)
