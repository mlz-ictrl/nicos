# pylint: skip-file

# test: setups = detbox_blackbox
# test: setupcode = SetDetectors(det_ikonl)

# take openbeam

maw(sty_huber, 1)

for i in range(2):
    openbeamimage(t=1)

maw(sty_huber, 0)

tomo(10, sry_huber, t=1)

printinfo('Tomo Finished!')

maw(shutter2, 'closed')
maw(shutter1, 'closed')

for i in range(2):
    darkimage(t=1)

printinfo('Test finished')
