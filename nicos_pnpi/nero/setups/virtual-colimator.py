description = 'Virtual colimator'

excludes = ['colimator']

x_gap_conf = configdata('localconfig.X_GAP_CONF')
y_gap_conf = configdata('localconfig.Y_GAP_CONF')
theta_s_conf = configdata('localconfig.THETA_S_CONF')
x_s_conf = configdata('localconfig.X_S_CONF')

dia1_angle_conf = configdata('localconfig.DIA1_ANGLE_CONF')
dia1_pos_conf = configdata('localconfig.DIA1_POS_CONF')
dia2_angle_conf = configdata('localconfig.DIA2_ANGLE_CONF')
dia2_pos_conf = configdata('localconfig.DIA2_POS_CONF')



devices = dict(
    x_gap = device('nicos.devices.generic.VirtualMotor',
                   description = x_gap_conf['description'],
                   precision = x_gap_conf['precision'],
                   lowlevel = x_gap_conf['lowlevel'],
                   abslimits = x_gap_conf['abslimits'],
                   speed = x_gap_conf['speed'],
                   unit = x_gap_conf['unit'],
                   ),

   y_gap = device('nicos.devices.generic.VirtualMotor',
                  description = y_gap_conf['description'],
                  precision = y_gap_conf['precision'],
                  lowlevel = y_gap_conf['lowlevel'],
                  abslimits = y_gap_conf['abslimits'],
                  speed = y_gap_conf['speed'],
                  unit = y_gap_conf['unit'],
                  ),

    col = device('nicos.devices.generic.TwoAxisSlit',
                 description = 'colimator gap',
                 horizontal = 'x_gap',
                 vertical = 'y_gap',
                 ),

    # shaper (polarizer)  rotation angle
    theta_s = device('nicos.devices.generic.VirtualMotor',
                     description = theta_s_conf['description'],
                     precision = theta_s_conf['precision'],
                     lowlevel = theta_s_conf['lowlevel'],
                     abslimits = theta_s_conf['abslimits'],
                     speed = theta_s_conf['speed'],
                     unit = theta_s_conf['unit'],
                     ),

    # shaper (polarizer) perpendicular of beam movement
    x_s = device('nicos.devices.generic.VirtualMotor',
                   description = x_s_conf['description'],
                   precision = x_s_conf['precision'],
                   lowlevel = x_s_conf['lowlevel'],
                   abslimits = x_s_conf['abslimits'],
                   speed = x_s_conf['speed'],
                   unit = x_s_conf['unit'],
                   ),

    dia1_angle = device('nicos.devices.generic.VirtualMotor',
                     description = dia1_angle_conf['description'],
                     precision = dia1_angle_conf['precision'],
                     lowlevel = dia1_angle_conf['lowlevel'],
                     abslimits = dia1_angle_conf['abslimits'],
                     speed = dia1_angle_conf['speed'],
                     unit = dia1_angle_conf['unit'],
                     ),


    dia1_pos = device('nicos.devices.generic.VirtualMotor',
                   description = dia1_pos_conf['description'],
                   precision = dia1_pos_conf['precision'],
                   lowlevel = dia1_pos_conf['lowlevel'],
                   abslimits = dia1_pos_conf['abslimits'],
                   speed = dia1_pos_conf['speed'],
                   unit = dia1_pos_conf['unit'],
                   ),

    dia2_angle = device('nicos.devices.generic.VirtualMotor',
                     description = dia2_angle_conf['description'],
                     precision = dia2_angle_conf['precision'],
                     lowlevel = dia2_angle_conf['lowlevel'],
                     abslimits = dia2_angle_conf['abslimits'],
                     speed = dia2_angle_conf['speed'],
                     unit = dia2_angle_conf['unit'],
                     ),


    dia2_pos = device('nicos.devices.generic.VirtualMotor',
                   description = dia2_pos_conf['description'],
                   precision = dia2_pos_conf['precision'],
                   lowlevel = dia2_pos_conf['lowlevel'],
                   abslimits = dia2_pos_conf['abslimits'],
                   speed = dia2_pos_conf['speed'],
                   unit = dia2_pos_conf['unit'],
                   ),
)


