description = 'Full operation setup'

group = 'basic'

includes = [
    'secoptic',
    'sampletable',
    'rc',
    'detector',
    'beamstop',
    'reactor',
]

startupcode = """
move(rc, 'on', fshutter, 'open', filter, 'in', collchanger, 'in', slit, (20, 30))
"""
