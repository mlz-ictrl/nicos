description = 'ASTOR setup'

group = 'basic'

modules = ['nicos.commands.imaging']

includes = ['shutters', 'sampletable', 'detector']

startupcode = '''
printinfo("Welcome to ASTOR.")
'''
