description = 'preset values for the resolution'
group = 'configdata'

RESOLUTION_PRESETS = {
    # NOTE: "ap" setting is (x_left, x_right, y_lower, y_upper)
    # TODO: instead of real motors of slit to use virtual ...
    '1x1mm':                 dict(ap=(1.30, -0.30, -2.50, 3.50), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '1.5mm':                 dict(ap=(1.55, -0.05, -2.25, 3.75), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '1.5mm-new':             dict(ap=(1.55, -0.05, -2.25, 3.75), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '2x2mm':                 dict(ap=(1.80,  0.20, -2.00, 4.00), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '2.5mm':                 dict(ap=(2.05,  0.45, -1.75, 4.25), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '3x3mm':                 dict(ap=(2.30,  0.70, -1.50, 4.50), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '3.5mm':                 dict(ap=(2.55,  0.95, -1.25, 4.75), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '4x4mm':                 dict(ap=(2.80,  1.20, -1.00, 5.00), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
    '5x5mm':                 dict(ap=(3.30,  1.70, -0.50, 5.50), det_x=-5.00, det_y=5.300, det_z=450, beamstop_x_in=27.5),
}
