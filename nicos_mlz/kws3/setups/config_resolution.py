description = 'preset values for the resolution'
group = 'configdata'

RESOLUTION_PRESETS = {
    # NOTE: "ap" setting is (x_left, x_right, y_lower, y_upper)
    # TODO: instead of real motors of slit to use virtual ...
    '1.0mm-VHRD-full':  dict(ap=(1.30, -0.30, -2.50, 3.50), det_x=12.0, det_y=1.00, det_z=450, beamstop_x_in=24.8),    
    '2x2mm-1m':  dict(ap=(1.80, 0.20, -2.00, 4.00), det_x=12.0, det_y=1.28, det_z=450, beamstop_x_in=28.2),
    '3.5mm':  dict(ap=(2.55,  0.95, -1.25, 4.75), det_x=12.0, det_y=1.10, det_z=450, beamstop_x_in=24.8),
}
