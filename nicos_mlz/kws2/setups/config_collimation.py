description = 'presets for the collimation guides and apertures'
group = 'configdata'

COLLIMATION_PRESETS = {
    '4m (45x45)':  dict(guides=4,  ap_x=45, ap_y=45),
   # '4m GISANS (30x5)':  dict(guides=4,  ap_x=30, ap_y=5),
   #'8m (45x45)':  dict(guides=8,  ap_x=45, ap_y=45),
    '8m (49x49)':  dict(guides=8,  ap_x=50, ap_y=50),
   # '8m GISANS (45x5)':  dict(guides=8,  ap_x=45, ap_y=5),
   # '8m GISANS (45x8)':  dict(guides=8,  ap_x=45, ap_y=8),
    #'8m (10x10)': dict(guides=8,  ap_x=10, ap_y=10),
    '20m (49x49)': dict(guides=20, ap_x=49, ap_y=49),
    '20m Lenses':  dict(guides=20, ap_x=4,  ap_y=4),
    '20m Trans':   dict(guides=20, ap_x=20, ap_y=20),
   # '20m (10x10)': dict(guides=20,  ap_x=10, ap_y=10),
#    '20m GISANS (45x20)': dict(guides=20,  ap_x=45, ap_y=20),
}
