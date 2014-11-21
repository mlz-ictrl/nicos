description = 'Double Crystal Monochromator'

group = 'optional'

includes = []

jcns_tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    mono = device('antares.monochromator.Monochromator',
                        description = 'ANTARES PG Double Crystal Monochromator',
                        dvalue1 = 3.354,
                        dvalue2 = 3.354,
                        distance = 97,
                        phi1 = 'mr1',
                        phi2 = 'mr2',
                        translation = 'mtz',
                        inout = 'mono_inout',
                        abslimits = (1.4, 6.5),
                        userlimits = (1.4, 6.5),
                        maxage = 5,
                        pollinterval = 3,
                        parkingpos = {
                                'phi1' : 12,
                                'phi2' : 12,
                                'translation' : -50,
                                'inout' : 'out',
                            },
                      ),
    mr1 = device('devices.taco.Motor',
                        speed = 5,
                        unit = 'deg',
                        description = 'Rotation of first monochromator crystal',
                        tacodevice = 'antares/copley/m11',
                        abslimits = (12, 66),
                        maxage = 5,
                        pollinterval = 3,
                      ),

    mr2 = device('devices.taco.Motor',
                        speed = 5,
                        unit = 'deg',
                        description = 'Rotation of second monochromator crystal',
                        tacodevice = 'antares/copley/m12',
                        abslimits = (12, 66),
                        maxage = 5,
                        pollinterval = 3,
                      ),

    mtz = device('devices.taco.Motor',
                        speed = 5,
                        unit = 'mm',
                        description = 'Translation of second monochromator crystal',
                        tacodevice = 'antares/copley/m13',
                        abslimits = (-120, 260),
                        userlimits = (-120, 260),
                        lowlevel = False,
                        maxage = 5,
                        pollinterval = 3,
                      ),


    mono_io = device('devices.tango.DigitalOutput',
                        unit = '',
                        description = 'Moves Monochromator in and out of beam',
                        tangodevice = '%s/antares/fzjdp_digital/Monochromator' % jcns_tango_host,
                        maxage = 5,
                        pollinterval = 3,
                        lowlevel = False,
                      ),

    mono_inout = device('devices.generic.Switcher',
                        description = 'Moves Monochromator in and out of beam',
                        moveable = 'mono_io',
                        mapping = { 'in':1, 'out':2 },
                        fallback = '<undefined>',
                        unit = '',
                        maxage = 5,
                        pollinterval = 3,
                        precision = 0,
                       ),
)

startupcode = '''
'''
