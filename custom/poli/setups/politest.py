description = 'Setup to test some parts of POLI'
group = 'lowlevel'

includes = ['detector', 'table', 'mono',]

devices = dict(
)

startupcode = """
printinfo("============================================================")
printinfo("Welcome to the POLI test setup.")
printinfo("Try doing an test scan, e.g.")
printinfo("  > scan(omega, -80, 0.2, 15, t=2)")
printinfo("  > scan(omega, -80, 0.05, 41, t=16)")
printinfo("============================================================")
"""
