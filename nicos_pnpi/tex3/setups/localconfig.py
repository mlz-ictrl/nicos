# setup file "localconfig.py"
# This is a configuration file for configuring device
# parameters and the base path of tango database

description = 'config file for setup properties of devices'

group = 'configdata'

tango_base = 'tango://server.tex3.pnpi:10000/'

# -------------------- Colimators --------------- #
COLX1_CONF = {
    'description': 'right horizontal damper of colimator',
    'precision': 0.01,                     # set precision for x1 damper
    'speed': 0.5,                          # unit of x1 damper
    'unit': 'mm',                          # set speed move of x1 damper
    'abslimits': (-50, 50),                # set absolute range limits ranges for x1 damper
    'lowlevel': False,                     # visible to the user
}


COLX2_CONF = {
    'description': 'left horizontal damper of colimator',
    'precision': 0.01,                     # set precision for x2 damper
    'speed': 0.5,                          # unit of x2 damper
    'unit': 'mm',                          # set speed move of x2 damper
    'abslimits': (-50, 50),                # set absolute range limits ranges for x2 damper
    'lowlevel': False,                     # visible to the user
}


COLY1_CONF = {
    'description': 'top vertical damper of colimator',
    'precision': 0.01,                     # set precision for y1 damper
    'speed': 0.5,                          # unit of y1 damper
    'unit': 'mm',                          # set speed move of y1 damper
    'abslimits': (-50, 50),                # set absolute range limits ranges for y1 damper
    'lowlevel': False,                     # visible to the user
}


COLY2_CONF = {
    'description': 'bottom vertical damper of colimator',
    'precision': 0.01,                     # set precision for y2 damper
    'speed': 0.5,                          # unit of y2 damper
    'unit': 'mm',                          # set speed move of y2 damper
    'abslimits': (-50, 50),                # set absolute range limits ranges for y2 damper
    'lowlevel': False,                     # visible to the user
}

# --------------- Sample Environment --------------- #
OMEGA_CONF = {
    'description': 'omega angle of sample environment',
    'precision': 0.01,                       # set precision for omega axis
    'unit': 'deg',                           # unit of omega axis
    'speed': 0.5,                            # set speed rotation of omega axis
    'abslimits': (-360, 360),                # set absolute range limits for omega axis
    'lowlevel': False,                       # visible to the user
}


PHI_CONF = {
    'description': 'phi angle of sample environment',
    'precision': 0.01,                     # set precision for phy axis
    'unit': 'deg',                         # unit of phy axis
    'speed': 0.5,                          # set speed rotation of phy axis
    'abslimits': (-360, 360),              # set absolute range limits for phy axis
    'lowlevel': False,                     # visible to the user
}


CHI_CONF = {
    'description': 'chi angle of sample environment',
    'precision': 0.01,                     # set precision for chi axis
    'unit': 'deg',                         # unit of chi axis
    'speed': 0.5,                          # set speed rotation of chi axis
    'abslimits': (-360, 360),              # set absolute range limits for chi axis
    'lowlevel': False,                     # visible to the user
}


THETA_CONF = {
    'description': 'theta angle of sample environment',
    'precision': 0.01,                     # set precision for theta axis
    'unit': 'deg',                         # unit of theta axis
    'speed': 0.5,                          # set speed rotation of theta axis
    'abslimits': (-360, 360),              # set absolute range limits for theta axis
    'lowlevel': False,                     # visible to the user
}

# --------------- Monochromator --------------- #
M_X_CONF = {
    'description': 'x coordinate of the monochromator moving table',
    'precision': 0.01,                     # set precision for x of monochromator axis
    'speed': 0.5,                          # unit of x monochromator axis
    'unit': 'mm',                          # set speed move of x monochromator axis
    'abslimits': (-50, 50),                # set absolute range limits for x of monochromator axis
    'lowlevel': False,                     # visible to the user
}


M_Y_CONF = {
    'description': 'y coordinate of the monochromator moving table',
    'precision': 0.01,                     # set precision for y of monochromator axis
    'speed': 0.5,                          # unit of y monochromator axis
    'unit': 'mm',                          # set speed move of y monochromator axis
    'abslimits': (-50, 50),                # set absolute range limits for y of monochromator axis
    'lowlevel': False,                     # visible to the user
}


M_Z_CONF = {
    'description': 'z coordinate of the monochromator moving table',
    'precision': 0.01,                     # set precision for z of monochromator axis
    'speed': 0.5,                          # unit of z monochromator axis
    'unit': 'mm',                          # set speed move of z monochromator axis
    'abslimits': (-50, 50),                # set absolute range limits for z of monochromator axis
    'lowlevel': False,                     # visible to the user
}

M_THETA_CONF = {
    'description': 'azimuth angle',
    'precision': 0.01,                     # set precision for theta of monochromator axis
    'unit': 'deg',                         # unit of theta monochromator axis
    'speed': 0.5,                          # set speed rotation of theta axis
    'abslimits': (-360, 360),              # set absolute range limits for theta axis
    'lowlevel': False,                     # visible to the user
}

M_ALPHA_CONF = {
    'description': 'zenith angle',
    'precision': 0.01,                     # set precision for alpha of monochromator axis
    'unit': 'deg',                         # unit of alpha monochromator axis
    'speed': 0.5,                          # set speed rotation of alpha monochromator axis
    'abslimits': (-360, 360),              # set absolute range limits for theta axis
    'lowlevel': False,                     # visible to the user
}
