description = 'Antrax plug switching box'

group = 'plugplay'

instrument_values = configdata('instrument.values')

tango_url = instrument_values['tango_url'] % setupname

devices = {
    '%s' % setupname : device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Plug switching device',
        tangodevice = tango_url + 'box/switchbox/switch',
        unit = '',
        mapping = {
            'off': 0,
            'on': 1,
        },
    ),
}
