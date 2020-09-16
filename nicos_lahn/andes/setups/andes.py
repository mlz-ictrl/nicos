description = 'ANDES setup'

group = 'basic'

# modules = []

includes = ['shutters', 'monochromator', 'sampletable', 'detector', 'detector_translation']

startupcode = '''
printinfo("Welcome to ANDES.")
'''

