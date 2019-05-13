# pylint: skip-file

# test: subdirs = frm2
# test: setups = 08_refsans, qmesydaq
# test: setupcode = SetDetectors(det)
# test: needs = configobj

# read all devices
read()

# get state of all devices
status()

# read some special devices
read(zb3.height, zb3.center)

# test count
count(1)
