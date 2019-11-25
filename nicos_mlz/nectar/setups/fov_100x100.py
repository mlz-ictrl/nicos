description = 'FOV linear axis for the small box (100 x 100)'

group = 'optional'

excludes = ['fov_190x190', 'fov_300x300']
includes = ['fov', 'frr']

startupcode = """
fov.userlimits = (16, 514)
"""
