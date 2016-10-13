description = 'plug-and-play magnet sample environment'
group = 'optional'

includes = ['alias_B']

devices = dict(
    B_virt            = device('devices.generic.VirtualMotor',
                               description = 'virtual "magnetic field"',
                               abslimits = (-10, 10),
                               unit = 'T'),

    garfield_onoff    = device('devices.generic.ManualSwitch',
                               description = 'on/off switch',
                               states = ['on', 'off'],
                              ),
    garfield_polarity = device('devices.generic.ManualSwitch',
                               description = 'polarity switch',
                               states = ['+1', '0', '-1'],
                              ),
    garfield_symmetry = device('devices.generic.ManualSwitch',
                               description = 'symmetry switch',
                               states = ['symmetric', 'short', 'unsymmetric'],
                              ),
    garfield_current  = device('devices.generic.VirtualMotor',
                               description = 'current source for garfield test',
                               abslimits = (0, 250),
                               unit = 'A',
                               ramp = 1.,
                              ),
    B_garfield        = device('frm2.amagnet.GarfieldMagnet',
                               description = 'magnetic field device, handling '
                                             'polarity switching and stuff',
                               currentsource = 'garfield_current',
                               onoffswitch = 'garfield_onoff',
                               polswitch = 'garfield_polarity',
                               symmetry = 'garfield_symmetry',
                               unit = 'T',
                               # B(I) = c[0]*I + c[1]*erf(c[2]*I) + c[3]*atan(c[4]*I)
                               calibrationtable = dict(
                                   symmetric = (0.00186517,
                                                0.0431937,
                                               -0.185956,
                                                0.0599757,
                                                0.194042),
                                   unsymmetric = (0.00136154,
                                                  0.027454,
                                                 -0.120951,
                                                  0.0495289,
                                                  0.110689),
                                   ),
                              ),

    magnet_current    = device('devices.generic.VirtualMotor',
                               description = 'current source for magnet test',
                               abslimits = (-250, 250),
                               unit = 'A',
                               ramp = 1.,
                              ),
    B_magnet          = device('devices.generic.CalibratedMagnet',
                               description = 'magnetic field device, handling '
                                             'polarity switching and stuff',
                               currentsource = 'magnet_current',
                               unit = 'T',
                               calibration = (0.000872603, -0.0242964, 0.0148907,
                                              0.0437158, 0.0157436),
                               abslimits = (-0.5, 0.5),
                              ),
)

alias_config = {
    'B': {'B_magnet': 100, 'B_garfield': 99, 'B_virt': 0},
}
