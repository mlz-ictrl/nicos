description = 'Pressure sensors'

group = 'optional'

#includes = ['alias_T']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    P_ng_elements = device('nicos.devices.tango.Sensor',
        description = 'Pressure in the neutron guide elements',
        tangodevice = '%s/pressure/ng_elements' % tango_base,
        fmtstr = '%.1f',
    ),
    P_polarizer = device('nicos.devices.tango.Sensor',
        description = 'Polarizer pressure',
        tangodevice = '%s/pressure/polarizer' % tango_base,
        fmtstr = '%.1f',
    ),
    P_selector_vacuum = device('nicos.devices.tango.Sensor',
        description = 'Selector vacuum pressure',
        tangodevice = '%s/pressure/selector_vacuum' % tango_base,
        fmtstr = '%.4f',
    ),
)
