description = 'PANDA setup for polarisation mode'

group = 'optional'

devices = dict(
    coil_1 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
                    description = 'Powersupply for horizontal field 1 at sample',
                    tangodevice = 'tango://phys.panda.frm2:10000/panda/coilps/supply13',
                    abslimits = (-10, 10),
                    # orientation = (6.1, 6.1, 0.0), # mT
                    orientation = (0.53, 0.53, 0.0), # mT - calibrated 20/11/2013
                    calibrationcurrent = 10,       #  A
                    lowlevel = True,
                   ),
    coil_2 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
                    description = 'Powersupply for horizontal field 2 at sample',
                    tangodevice = 'tango://phys.panda.frm2:10000/panda/coilps/supply23',
                    abslimits = (-10, 10),
                    # orientation = (6.1, -6.1, 0.0),# mT
                    orientation = (0.53, -0.53, 0.0),# mT - calibrated 20/11/2013
                    calibrationcurrent = 10,       # A
                    lowlevel = True,
                   ),
    coil_3 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
                    description = 'Powersupply for vertical field at sample',
                    tangodevice = 'tango://phys.panda.frm2:10000/panda/coilps/supply14',
                    abslimits = (-10, 10),
                    # orientation = (0., 0., 55.5),  # mT
                    orientation = (0, 0, 11.65),  # mT - calibrated 20/11/2013
                    calibrationcurrent = 10,       # A
                    lowlevel = True,
                   ),
    gf = device('nicos_mlz.panda.devices.guidefield.GuideField',
                description = 'Vector field at sample location',
                alpha = 'alphastorage',
                coils = ['coil_1', 'coil_2', 'coil_3'],
                field = 10,    # mT
                mapping= {'off'   : None,
                          'perp'  : ( 1., 0., 0.),
                          '-perp' : (-1., 0., 0.),
                          'par'   : ( 0., 1., 0.),
                          '-par'  : ( 0.,-1., 0.),
                          'z'     : ( 0., 0., 1.),
                          '-z'    : ( 0., 0.,-1.),
                          'up'    : ( 0., 0., 1.),
                          'down'  : ( 0., 0.,-1.),
                          '0'     : ( 0., 0., 0.),
                         },
               ),
    sf1   = device('nicos.devices.polarized.KFlipper',
                   description = 'Spin Flipper 1 (before sample)',
                   flip = 'sf1_f',
                   corr = 'sf1_c',
                   kvalue = 'ki',
                   flipcurrent = [-0.18037, -0.43804],
                   compcurrent = 2.35,
                  ),
    sf2   = device('nicos.devices.polarized.KFlipper',
                   description = 'Spin Flipper 2 (after sample)',
                   flip = 'sf2_f',
                   corr = 'sf2_c',
                   kvalue = 'kf',
                 # for kf=1.55+befilter
                   flipcurrent = [0.083,0.38],
                   compcurrent = 1.45,
                 #~ # for kf=1.94 +/-pg
                 #~ flipcurrent = [0.765, 0],
                 #~ compcurrent = 2.4474,
                  ),
    sf1_f = device('nicos.devices.tango.PowerSupply',
                   description = 'flipper 1 flipping current',
                   tangodevice = 'tango://phys.panda.frm2:10000/panda/coilps/supply21',
                   abslimits = (-4, 4),
                   userlimits = (-3, 3),
                   unit = 'A',
                   lowlevel = True,
                  ),
    sf1_c = device('nicos.devices.tango.PowerSupply',
                   description = 'flipper 1 compensation current',
                   tangodevice = 'tango://phys.panda.frm2:10000/panda/coilps/supply22',
                   abslimits = (-4, 4),
                   userlimits = (-3, 3),
                   unit = 'A',
                   lowlevel = True,
                  ),

    sf2_f = device('nicos.devices.tango.PowerSupply',
                   description = 'flipper 2 flipping current',
                   tangodevice = 'tango://phys.panda.frm2:10000/panda/coilps/supply11',
                   abslimits = (-4, 4),
                   userlimits = (-3, 3),
                   unit = 'A',
                   lowlevel = True,
                  ),
    sf2_c = device('nicos.devices.tango.PowerSupply',
                   description = 'flipper 2 compensation current',
                   tangodevice = 'tango://phys.panda.frm2:10000/panda/coilps/supply12',
                   abslimits = (-4, 4),
                   userlimits = (-3, 3),
                   unit = 'A',
                   lowlevel = True,
                  ),
)

startupcode = '''
printwarning('Please check powersupply addresses carefully after mounting flippers!!!')
'''
