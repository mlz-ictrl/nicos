# move to initial position
maw(tx, 0, ty, -4, tz, 0, rz, 0, rx, 0, ry, 0, omega, -1, detarm, 5)

for speed in [1, 2, 3, .1, .5]:
    pause("kinematic scan omega between -1..5 with %f deg/s" % speed)
    kscan(omega, -1, 6, 2, speed)  # from -1 to 5 and back to -1

pause("Move omega and rz to initial position")
maw(omega, 0, rz, 1)
for speed in [1, 2, 3, .1, .5]:
    pause("kinematic scan rz between 1..-5 with %f deg/s" % speed)
    kscan(rz, 1, -6, 2, speed)  # from 1 to -5 and back to 1
maw(rz, 0)