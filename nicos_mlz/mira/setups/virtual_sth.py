description = 'virtual sample table motor'
group = 'optional'

includes = ['alias_sth']

devices = dict(
    sth_virtual = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual sample theta angle for powder experiments',
        abslimits = (-360, 360),
        unit = 'deg',
    ),
)

alias_config = {
    'sth': {'sth_virtual': 100},
}
