description = 'config file for setup properties of devices for Nero machine'

group = 'configdata'

tango_base = 'tango://server.nero.pnpi:10000/'

# --------------- Sample Environment --------------- #
ALPHA_CONF = {
    'description': 'azimuth angle of the sample table',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'deg',
    'abslimits': (-360, 360),
    'lowlevel': False,
}

#  B(I) = Ic0 + c1*erf(c2*I) + c3*atan(c4*I)
#  calibration: (c0, c1, c2, c3, c4)
B_CONF = {
    'description': 'Magnet field [T]',
    'calibration': (0.1, 0.0, 0.0, 0.0, 0.0),
}

CURRENT_CONF = {
    'description': 'Current source for magnet field',
    'abslimits': (0, 15),
    'lowlevel': True,
    'unit': 'A',
}

# --------------- Monochromator --------------- #
X_CONF = {
    'description': 'x position of the monochromator table',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'mm',
    'abslimits': (-100, 100),
    'lowlevel': False,
}

Y_CONF = {
    'description': 'y position of the monochromator table',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'mm',
    'abslimits': (-100, 100),
    'lowlevel': False,
}

CHI1_CONF = {
    'description': 'angle of the first crystal of the monochromator',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'arcmin',
    'abslimits': (-120, 120),
    'lowlevel': False,
}

CHI2_CONF = {
    'description': 'angle of the second crystal of the monochromator',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'arcmin',
    'abslimits': (-120, 120),
    'lowlevel': False,
}

CHI3_CONF = {
    'description': 'angle of the third crystal of the monochromator',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'arcmin',
    'abslimits': (-120, 120),
    'lowlevel': False,
}

CHI4_CONF = {
    'description': 'angle of the fourth crystal of the monochromator',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'arcmin',
    'abslimits': (-120, 120),
    'lowlevel': False,
}

OMEGA_CONF = {
    'description': 'azimuth angle of the sample table',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'deg',
    'abslimits': (-90, 90),
    'lowlevel': False,
}

# --------------- Colimator --------------- #
X_GAP_CONF = {
    'description': 'y position of the monochromator table',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'mm',
    'abslimits': (-100, 100),
    'lowlevel': True,
}

Y_GAP_CONF = {
    'description': 'y position of the monochromator table',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'mm',
    'abslimits': (-100, 100),
    'lowlevel': True,
}
