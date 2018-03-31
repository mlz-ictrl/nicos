description = 'debug MP only'

group = 'basic'

includes = ['reactor','nl2b',
            # 'fak40', 'guidehall', 'memograph',
            # 'shutter',
            # 'shutter_gamma',
            # 'det_pivot', 'det_table', 'det_yoke',
            # 'det_pos',
            # 'optic_x',
            # 'sample',
            # 'gonio',
            # 'poti_ref',
            # 'pumpstand',
            # 'vacuum',
            # 'prim_monitor',
            # 'mode',
            # 'optic',
            # 'optic_ele',
            # 'optic_elements',
            ]

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
