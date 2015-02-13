description = 'Axels diamond setup'

group = 'optional'

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    lin = device('devices.taco.Motor',
                 description = 'linear axis',
                 tacodevice = 'antares/copley/m10',
                 abslimits = (-25, 25),
                 userlimits = (-25, 25),
                ),
    rot = device('devices.taco.Motor',
                 description = 'rotation axis',
                 tacodevice = 'antares/copley/m11',
                 abslimits = (-99999, 99999),
                 userlimits = (-99999, 99999),
                ),
)
