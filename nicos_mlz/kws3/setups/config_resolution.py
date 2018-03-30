description = 'preset values for the resolution'
group = 'configdata'

RESOLUTION_PRESETS = {
    # NOTE: "ap" setting is (x_left, x_right, y_lower, y_upper)
    # TODO: instead of real motors of slit to use virtual ...
    '0.7mm-VHRD':            dict(ap=(1.15, -0.45, -2.65, 3.35), det_x=8.0,  det_y=0.1,  det_z=450, beamstop_x_in=24.8),
    '0.5x5.0-VHRD-grating':  dict(ap=(1.05, -0.55, -0.50, 5.50), det_x=8.0,  det_y=0.1,  det_z=450, beamstop_x_in=24.8),
    '1.0mm-VHRD-full':       dict(ap=(1.30, -0.30, -2.50, 3.50), det_x=12.0, det_y=1.0,  det_z=450, beamstop_x_in=24.8),
    '1.5mm':                 dict(ap=(1.55, -0.05, -2.25, 3.75), det_x=11.0, det_y=0.95, det_z=450, beamstop_x_in=24.8),
    '2x2mm':                 dict(ap=(1.80,  0.20, -2.00, 4.00), det_x=10.0, det_y=1.0,  det_z=450, beamstop_x_in=28.2),
    '3mm':                   dict(ap=(2.30,  0.70, -1.50, 4.50), det_x=10.0, det_y=0.9,  det_z=450, beamstop_x_in=28.2),
    '3.5mm':                 dict(ap=(2.55,  0.95, -1.25, 4.75), det_x=12.0, det_y=1.28, det_z=450, beamstop_x_in=24.8),
}
