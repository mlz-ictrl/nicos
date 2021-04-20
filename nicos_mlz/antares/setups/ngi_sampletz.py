description = 'nGI Sample Stage'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    nGI_sampletz = device('nicos.devices.entangle.Motor',
        speed = 5,
        unit = 'mm',
        description = 'Movement of Sample in beam direction',
        tangodevice = tango_base + 'copley/m11',
        abslimits = (0, 295),
        userlimits = (0, 295),
        maxage = 5,
        pollinterval = 3,
        precision = 0.1,
    ),
)
