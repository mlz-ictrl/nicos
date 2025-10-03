description = 'Sample lift for 1T electromagnet'

display_order = 53

pvprefix = 'SQ:AMOR:mmac1:'

excludes = ['stz_table']

devices = dict(
    smz = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Sample lift with magnet installed',
        motorpv = pvprefix + 'smz',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
)

alias_config = {'sz': {'smz': 10}}

