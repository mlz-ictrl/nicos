# pylint: skip-file

# test: setups = antares_s, detector_neo
# test: setupcode = SetDetectors(det_neo)

# take openbeam

maw(sty_huber, 1)

for i in range(2):
    openbeamimage(t=1)

maw(sty_huber, 0)

tomo(10, 'sry_huber', t=1)

printinfo('Tomo Finished!')

maw(shutter2, 'closed')
maw(shutter1, 'closed')

for i in range(2):
    darkimage(t=1)

printinfo('Test finished')
