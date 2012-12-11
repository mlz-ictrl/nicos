description = 'minimal NICOS startup setup'
group = 'lowlevel'

includes = ['tas', 'detector', 'temperature']

startupcode = '''
printinfo("============================================================")
printinfo("Welcome to the NICOS demo setups.")
printinfo("This demo is configured as a virtual triple-axis instrument.")
printinfo("Try doing an elastic scan over a Bragg peak, e.g.")
printinfo("  qcscan((1, 0, 0, 0), (0.002, 0, 0, 0), 10, t=1, kf=1.55)")
printinfo("or an energy scan, e.g.")
printinfo("  qscan((1, 0.2, 0, 4), (0, 0, 0, 0.2), 21, t=1, kf=2)")
printinfo("============================================================")
'''
