description = 'presets for the collimation guides and apertures'
group = 'configdata'

COLLIMATION_PRESETS = {
    '2m (30x30)':   dict(guides=2,  ap_x=30,   ap_y=30),
    '4m (30x30)':   dict(guides=4,  ap_x=30,   ap_y=30),
    '8m (30x30)':   dict(guides=8,  ap_x=30,   ap_y=30),
    '8m (6x6) Tr':  dict(guides=8,  ap_x=6,    ap_y=6),
    '14m (30x30)':  dict(guides=14, ap_x=30,   ap_y=30),
    '20m (30x30)':  dict(guides=20, ap_x=30,   ap_y=30),
    '2m (50x50)':   dict(guides=2,  ap_x=50,   ap_y=49.9),
    '4m (50x50)':   dict(guides=4,  ap_x=49.9, ap_y=49.9),
    '4m (10x15) GISANS':  dict(guides=4,  ap_x=10, ap_y=15),
    '8m (10x15) GISANS':  dict(guides=8,  ap_x=10, ap_y=15),
    '14m (10x15) GISANS': dict(guides=14, ap_x=10, ap_y=15),
    '20m (10x15) GISANS': dict(guides=20, ap_x=10, ap_y=15),
}
