# -*- coding: utf-8 -*-

description = 'JCNS motor control'

group = 'optional'

includes = ['jcns_io']

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    cryo_vertical = device('devices.tango.Motor',
                         description = 'Flex Achse 1',
                         tangodevice = '%s/antares/fzjs7/Flex_Achse_1' % tango_host,
                         abslimits = (-500000, 500000),
                         unit = 'microsteps',
                        ),

    cryo_horizontal = device('devices.tango.Motor',
                         description = 'Flex Achse 2',
                         tangodevice = '%s/antares/fzjs7/Flex_Achse_2' % tango_host,
                         abslimits = (-500000, 500000),
                         unit = 'microsteps',
                        ),

    cryo_rotation = device('devices.tango.Motor',
                         description = 'Flex Achse 3',
                         tangodevice = '%s/antares/fzjs7/Flex_Achse_3' % tango_host,
                         abslimits = (0, 360),
                         unit = 'deg',
                        ),

    # monochromator. monoswitch is defined in jcns_io.py
    mono_linear = device('devices.tango.Motor',
                         description = 'Monochromator translation',
                         tangodevice = '%s/antares/fzjs7/Mono_linear' % tango_host,
                        ),

    mono_phi1 = device('devices.tango.Motor',
                       description = 'Monochromator 1 rotation',
                       tangodevice = '%s/antares/fzjs7/Mono_phi1' % tango_host,
                      ),

    mono_phi2 = device('devices.tango.Motor',
                       description = 'Monochromator 2 rotation',
                       tangodevice = '%s/antares/fzjs7/Mono_phi2' % tango_host,
                      ),

    mono = device('antares.monochromator.Monochromator',
                  description = 'Monochromator device',
                  phi1 = 'mono_phi1',
                  phi2 = 'mono_phi2',
                  translation = 'mono_linear',
                  inout = 'monoswitch',
                  dvalue1 = 3.355,     # for PG
                  dvalue2 = 3.355,     # for PG
                  distance = 10.3,   # bogus value
                  tolphi = 0.01,
                  toltrans = 0.01,
                  unit = 'A',
                  abslimits = (2.7, 6.5),
                  parkingpos = {
                          'phi1' : 12,
                          'phi2' : 12,
                          'translation' : -50,
                          'inout' : 'out',
                      },
                 ),

    periscope_linear = device('devices.tango.Motor',
                              description = 'Periscope linear motion',
                              tangodevice = '%s/antares/fzjs7/Periskop_linear' % tango_host,
                             ),

    periscope_rot_1 = device('devices.tango.Motor',
                             description = 'Periscope rotation 1',
                             tangodevice = '%s/antares/fzjs7/Periskop_rot_1' % tango_host,
                            ),

    periscope_rot_2 = device('devices.tango.Motor',
                             description = 'Periscope rotation 2',
                             tangodevice = '%s/antares/fzjs7/Periskop_rot_2' % tango_host,
                            ),

    selector_linear = device('devices.tango.Motor',
                             description = 'Selector translation',
                             tangodevice = '%s/antares/fzjs7/Selektor_linear' % tango_host,
                            ),

    # filterwheel. filterwheel_inout is defined in jcns_io.py
    filterwheel_mot = device('devices.tango.Motor',
                             tangodevice = '%s/antares/fzjs7/Filterrad' % tango_host,
                             precision = 0.,
                             lowlevel = True,
                            ),

    filterwheel = device('devices.generic.MultiSwitcher',
                         description = 'Filterwheel, moves automatical into the beam, if needed',
                         moveables = ['filterwheel_mot','filterwheel_inout'],
                         mapping = dict( bi_mono=[1, 'in'],
                                         sapphire=[2, 'in'],
                                         bi_poly=[3, 'in'],
                                         be=[4, 'in'],
                                         out=[2,'out']
                                       ),
                         precision = [0, 0],
                         blockingmove = True,
                        ),
)

startupcode = '''
'''
