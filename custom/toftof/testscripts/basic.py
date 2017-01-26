# pylint: skip-file

# test: subdirs = frm2
# test: setups = toftof
# test: setupcode = SetDetectors(det)

# read some special devices

read(chSpeed)
read(chWL)
read(chRatio)

read(slit)
read(ngc)
read(rc_onoff)


# test count

count(200)
