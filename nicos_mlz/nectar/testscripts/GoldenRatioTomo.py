# pylint: skip-file
# GoldenRatioTomo 1.1

# test: needs = tango
# test: needs = astropy
# test: setups = nectar, servostar, detector
# test: setupcode = SetDetectors(det)

import math

printinfo('This tomo covers all angles for the golden ratio for 360 deg')
NewSample('TestSample_DEF')
Remark('Filter 4, Multileaf 30x50mm')

printinfo('Acquire openbeam and di images')
maw(sty, 1.0)
maw(stx, 1.0)

for i in range(2):
    darkimage(t=1)

for i in range(2):
    openbeamimage(t=1)
printinfo('finished post OB and DI')

maw(stx, 10)
maw(sty, 10)
printinfo('aligned sample and start Tomo')

grtomo(10, sry, t=1)

print('Tomo Finished!')
print('Test finished')
