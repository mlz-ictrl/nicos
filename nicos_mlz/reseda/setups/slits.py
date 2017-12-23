#  -*- coding: utf-8 -*-

description = 'Slits/Pinholes'
group = 'optional'
display_order = 4
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    pinhole5 = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Pinhole 5mm radius',
        tangodevice = '%s/iobox/plc_pinhole5' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
    pinhole10 = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Pinhole 10mm radius',
        tangodevice = '%s/iobox/plc_pinhole10' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
    slit = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Slit 10x40mm',
        tangodevice = '%s/iobox/plc_slit' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
)
