description = 'preset values for the resolution'
group = 'configdata'

RESOLUTION_PRESETS = {
    # NOTE: "ap" setting is (x_left, x_right, y_lower, y_upper)
    # TODO: instead of real motors of slit to use virtual ...
    '1.5mm':   dict(ap=(1.55, -0.05, -2.25, 3.75), det_x=4.5, det_y=0.91, det_z=450, beamstop_x_in=24.8),
    '3.0mm':   dict(ap=(2.30,  0.70, -1.50, 4.50), det_x=4.5, det_y=0.91, det_z=450, beamstop_x_in=24.8),
    '1.5mm-center':   dict(ap=(1.55, -0.05, -2.25, 3.75), det_x=1.5, det_y=1.00, det_z=450, beamstop_x_in=24.8),
    '2.0mm-center':   dict(ap=(1.80,  0.20, -2.00, 4.00), det_x=1.5, det_y=1.00, det_z=450, beamstop_x_in=24.8),
    '3.0mm-center':   dict(ap=(2.30,  0.70, -1.50, 4.50), det_x=1.5, det_y=1.00, det_z=450, beamstop_x_in=24.8),
    '4.0mm-center':   dict(ap=(2.80,  1.20, -1.00, 5.00), det_x=1.5, det_y=1.00, det_z=450, beamstop_x_in=24.8),
    '5.0mm-gisans-0.2grd':   dict(ap=(3.30,  1.70, -0.50, 5.50), det_x=25.0, det_y=6.3, det_z=450, beamstop_x_in=24.8),
    '2.0mm-center-1m':   dict(ap=(1.80,  0.20, -2.00, 4.00), det_x=1.5, det_y=1.18, det_z=450, beamstop_x_in=24.8),
}
