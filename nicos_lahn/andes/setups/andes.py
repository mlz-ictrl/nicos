description = 'ANDES setup'

group = 'basic'

modules = ['nicos_lahn.commands.basic']

includes = ['shutters', 'monochromator', 'sampletable', 'detector']

startupcode = '''
printinfo("Welcome to ANDES.")
read()
'''

