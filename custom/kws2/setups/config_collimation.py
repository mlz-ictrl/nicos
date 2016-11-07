description = 'presets for the collimation guides and apertures'
group = 'configdata'

# KWS2TODO: copy collimation presets from kwsconfig

COLLIMATION_PRESETS = {
    '2m (30x30)':  dict(guides=2,  ap_x=30, ap_y=30),
    '4m (30x30)':  dict(guides=4,  ap_x=30, ap_y=30),
    '8m (30x30)':  dict(guides=8,  ap_x=30, ap_y=30),
    '14m (30x30)': dict(guides=14, ap_x=30, ap_y=30),
    '20m (30x30)': dict(guides=20, ap_x=30, ap_y=30),
    '2m (50x50)':  dict(guides=2,  ap_x=50, ap_y=49.9),
    '4m (50x50)':  dict(guides=4,  ap_x=49.9, ap_y=49.9)
}
