# pylint: skip-file


# take openbeam

maw(sty_huber, 1)

for i in range(2):
    openbeamimage(t=1)

maw(sty_huber, 0)

tomo(10, 'sry_huber', t=1)

print('Tomo Finished!')

maw(shutter2, 'closed')
maw(shutter1, 'closed')

for i in range(2):
    darkimage(t=1)

print('Test finished')
