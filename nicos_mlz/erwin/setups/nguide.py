description = 'Erwin neutron guide devices'
group = 'optional'

tango_base = 'tango://nguidectrl.spodi.frm2.tum.de:10000/box/'

devices = dict(
    p1_nguide = device('nicos.devices.entangle.Sensor',
        description = 'Pressure 1',
        tangodevice = tango_base + 'leybolde/sensor1',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
        warnlimits = (None, 10),
    ),
    p2_nguide = device('nicos.devices.entangle.Sensor',
        description = 'Pressure 2',
        tangodevice = tango_base + 'leybolde/sensor2',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
        warnlimits = (None, 10),
    ),
    p3_nguide = device('nicos.devices.entangle.Sensor',
        description = 'Pressure 3',
        tangodevice = tango_base + 'leybolde/sensor3',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
        warnlimits = (None, 10),
    ),
    pump = device('nicos_mlz.erwin.devices.pump.Pump',
        description = 'Neutron guide pump',
        tangodevice = tango_base + 'pump/pump',
    ),
)

display_order = 100

monitor_blocks = dict(
    default = Block('Neutron Guide', [
        BlockRow(
            Field(name='p1 N-Guide', dev='p1_nguide'),
            Field(name='p2 N-Guide', dev='p2_nguide'),
            Field(name='p3 N-Guide', dev='p3_nguide'),
            ),
        ],
        setups=setupname,
    ),
)
