# pylint: skip-file

# test: subdirs = laue
# test: setups = laue
# test: setupcode = SetDetectors(det1)
# test: setupcode = maw(sampleslit, 1)

# read all devices
read()

maw(omega, 2)

# count: Manually check if image looks OK (liveView, tif with external app)
count(10)
