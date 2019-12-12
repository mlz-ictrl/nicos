description = 'FOV linear axis for the large box (300 x 300)'

group = 'optional'

excludes = ['fov_100x100', 'fov_190x190']
includes = ['fov', 'frr']

startupcode = """
fov.userlimits = (220, 950)
"""
