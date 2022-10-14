description = 'filter selector setup'

group = 'lowlevel'

tango_base = 'tango://lahn:10000/astor/'

devices = dict(
    crystal_m=device('nicos.devices.entangle.Motor',
                     description='filter changer rotation',
                     tangodevice=tango_base + 'filter/crystal',
                     visibility=(),
                     ),
    crystal=device('nicos.devices.generic.Switcher',
                   description='filter changer',
                   moveable='crystal_m',
                   mapping={
                       'empty': 0,
                       'Beryl': 60,
                       'Cd': 120,
                       'Sapphire': 180,
                       'Single Crystal Bi': 240,
                       'Polycrystaline Bi': 300,
                   },
                   precision=0,
                   requires={'level': 'admin'},
                   ),
)
