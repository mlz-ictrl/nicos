# move to initial position
maw(tx, 0, ty, -4, tz, 0, rz, 0, rx, 0, ry, 0, omega, 0, detarm, 0)

pause("Scan t2t 0..1 in steps of 0.1 with count time 2s.")
sscan(t2t, 0, .1, 1, 2.0)
pause("Move t2t to 0.")
maw(t2t, 0)

pause("Scan ty -5..5 in steps of 0.5 with count time 1s.")
sscan(ty, -5, .5, 5, 1.0)
pause("Move ty to 0.")
maw(ty, 0)

pause("Scan tx -5..5 in steps of 0.5 with count time 1s.")
sscan(tx, -5, .5, 5, 1.0)
pause("Move tx to 0.")
maw(tx, 0)

pause("Scan tz -20..20 in steps of 1 with count time 1s.")
sscan(tz, -20, 1, 20, 1.0)
pause("Move tz to 0.")
maw(tz, 0)

pause("Scan ry -3..3 in steps of .5 with count time 1s.")
sscan(ry, -3, .5, 3, 1.0)
pause("Move ry to 0.")
maw(ry, 0)

pause("Move detarm into guide - emergency stop penetration test.")
maw(detarm, -10)