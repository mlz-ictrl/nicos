# move to initial position
maw(tx, 0, ty, -4, tz, 0, rz, 0, rx, 0, ry, 0, omega, 0, detarm, 0)

pause("Check ty boundaries.")
maw(ty, -45)
maw(ty, 45)
maw(ty, 0)

pause("Check tx boundaries.")
maw(tx, -75)
maw(tx, 75)
maw(tx, 0)

pause("Check ry boundaries.")
maw(ry, -5)
maw(ry, 5)
maw(ry, 0)