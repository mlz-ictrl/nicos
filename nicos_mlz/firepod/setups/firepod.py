description = 'Full operation setup'

group = 'basic'

includes = [
    'slits',
    'sampletable',
    'rc',
    'detector',
    'distances',
    'optic',
]

startupcode = """
move(rc, 'on', shutter, 'open', filter, 'in', collimator, 'in', slit, (20, 30))
"""
