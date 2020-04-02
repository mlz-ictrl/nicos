description = "sc2 height after nok9"

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']

devices = dict(
    sc2 = device('nicos.devices.tango.Motor',
        description = 'sc2 Motor; has brake, will move down to mech. limit if '
                      'brake and control are off, this will kill the system '
                      '2019-05-29 photo',
        tangodevice = tango_base + 'optic/sc2/motor',
        refpos = -7.2946,
    ),
)
