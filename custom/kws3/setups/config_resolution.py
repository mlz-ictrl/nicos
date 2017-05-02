description = 'preset values for the resolution'
group = 'configdata'

RESOLUTION_PRESETS = {
    # NOTE: "ap" setting is (x_left, x_right, y_lower, y_upper)
    # TODO: instead of real motors of slit to use virtual ...
    'p1mm':   dict(ap=(0.5, 0.5, 0.5, 0.5), det_x=0, det_y=2, det_z=450, beamstop_x_in=0),
    'p2mm':   dict(ap=(1.0, 1.0, 1.0, 1.0), det_x=0, det_y=2, det_z=450, beamstop_x_in=0),
    'p5mm':   dict(ap=(2.5, 2.5, 2.5, 2.5), det_x=0, det_y=2, det_z=450, beamstop_x_in=0),
}
