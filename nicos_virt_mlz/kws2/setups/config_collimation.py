description = 'presets for the collimation guides and apertures'
group = 'configdata'

COLLIMATION_PRESETS = {
    '4m (30x30)':  dict(guides=4,  ap_x=30, ap_y=30),
    '8m (50x50)':  dict(guides=8,  ap_x=50, ap_y=50),
    '14m (50x50)': dict(guides=14, ap_x=50, ap_y=50),
    '20m (50x50)': dict(guides=20, ap_x=49, ap_y=49),
    # '20m Lenses':  dict(guides=20, ap_x=4,  ap_y=4),
    '20m Trans':   dict(guides=20, ap_x=20, ap_y=20),
    '20m (10x10)': dict(guides=20,  ap_x=10, ap_y=10),
}
