description = 'presets for the collimation guides and apertures'
group = 'configdata'

COLLIMATION_PRESETS = {
    '4m (30x30)':  dict(guides=4,  ap_x=30, ap_y=30),
    '8m (45x45)':  dict(guides=8,  ap_x=45, ap_y=45),
    '20m (45x45)': dict(guides=20, ap_x=45, ap_y=45),
    '20m Lenses':  dict(guides=20, ap_x=3,  ap_y=3),
    '20m Trans':   dict(guides=20, ap_x=20, ap_y=20),
}
