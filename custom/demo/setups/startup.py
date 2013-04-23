description = 'NICOS demo startup setup'
group = 'lowlevel'

startupcode = '''
printinfo("============================================================")
printinfo("Welcome to the NICOS demo.")
printinfo("Run one of the following commands to set up either a triple-axis")
printinfo("or a SANS demo setup:")
printinfo("  > NewSetup('tas')")
printinfo("  > NewSetup('sans')")
'''
