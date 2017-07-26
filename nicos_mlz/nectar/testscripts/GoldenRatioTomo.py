# pylint: skip-file
# GoldenRatioTomo 1.1

import math

print('This tomo covers all angles for the golden ratio for 360 deg')
NewSample('TestSample_DEF')
Remark('Filter 4, Multileaf 30x50mm')

print('Acquire openbeam and di images')
maw(sty, 1.0)
maw(stx, 1.0)

for i in range(2):
    darkimage(t=1)

for i in range(2):
    openbeamimage(t=1)
print('finished post OB and DI')

maw(stx, 10)
maw(sty, 10)
print('aligned sample and start Tomo')

with manualscan(sry):
    for i in range(6):
        # Calculate the angle
        angle = (i*(1+math.sqrt(5))/2)*(math.pi*2) % (math.pi*2)
        angledegrees = math.degrees(angle)
        print('Moving to angle: %.2f, Iteration Step: %d', (angledegrees, i))
        maw(sry, angledegrees)
        count(1)
