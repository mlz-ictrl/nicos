description = 'preset values for the resolution'
group = 'configdata'

RESOLUTION_PRESETS = {
    # NOTE: "ap" setting is (x_left, x_right, y_lower, y_upper)
    # TODO: instead of real motors of slit to use virtual ...
    '0.6mmx12.0mm-center':   dict(ap=(0.80, -0.2, 3.00, 9.00), det_x=4.5, det_y=0.70, det_z=450,beamstop_x_in=28.5),
    '6.0mmx0.1mm-center':   dict(ap=(3.50, 2.50, -2.95, 3.05), det_x=4.5, det_y=0.70, det_z=450,beamstop_x_in=28.5),
    '0.6mmx0.6mm-center':   dict(ap=(0.80, -0.20, -2.70, 3.30), det_x=4.5, det_y=0.70, det_z=450,beamstop_x_in=28.5),
    '1.5mmx1.5mm-center':   dict(ap=(1.25, 0.25, -2.25, 3.75), det_x=4.5, det_y=0.70, det_z=450,beamstop_x_in=28.5),
    '2mmx2mm-center':   dict(ap=(1.50, 0.50, -2.00, 4.00), det_x=4.5, det_y=0.70, det_z=450, beamstop_x_in=28.5),
    '2mmx2mm-1m':   dict(ap=(1.50, 0.50, -2.00, 4.00), det_x=4.5, det_y=0.00, det_z=450, beamstop_x_in=28.5),
    '3mmx3mm-center':   dict(ap=(2.00, 1.00, -1.50, 4.50), det_x=4.5, det_y=0.70, det_z=450, beamstop_x_in=28.5),
    '3mmx3mm-BS':   dict(ap=(2.00, 1.00, -1.50, 4.50), det_x=4.5, det_y=0.91, det_z=450, beamstop_x_in=28.65),
    '2mmx2mm-BS':   dict(ap=(1.50, 0.50, -2.00, 4.00), det_x=4.5, det_y=0.91, det_z=450, beamstop_x_in=28.65),
    '10mmx10mm-center':   dict(ap=(5.50, 4.50, 2.00, 8.00), det_x=4.5, det_y=0.70, det_z=450, beamstop_x_in=28.5),
    '10mmx10mm-offcenter':   dict(ap=(5.50, 4.50, 2.00, 8.00), det_x=4.5, det_y=3.00, det_z=450, beamstop_x_in=28.5),
    '3mmx3mm-off-center':   dict(ap=(2.00, 1.00, -1.50, 4.50), det_x=4.5, det_y=0.00, det_z=450, beamstop_x_in=28.5),
    '1mmx1mm':   dict(ap=(5, -4, -4, 5), det_x=-2.5, det_y=1.70, det_z=300, beamstop_x_in=28.5),
    '2mmx2mm':   dict(ap=(5.5, -3.5, -3.5, 5.5), det_x=-2.5, det_y=1.70, det_z=300, beamstop_x_in=28.5),
    '3mmx3mm':   dict(ap=(6.0, -3.0, -3.0, 6.0), det_x=-2.5, det_y=1.70, det_z=300, beamstop_x_in=28.5),
    '5mmx5mm':   dict(ap=(7.0, -2.0, -2.0, 7.0), det_x=-2.5, det_y=1.70, det_z=300, beamstop_x_in=28.5),
}
