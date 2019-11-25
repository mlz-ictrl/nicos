description = 'FOV linear axis for the medium box (190 x 190)'

group = 'optional'

excludes = ['fov_100x100', 'fov_300x300']
includes = ['fov', 'frr']

startupcode = """
fov.userlimits = (160, 669)
"""
