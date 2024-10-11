# pylint: skip-file

# test: needs = tango
# test: subdirs = poli
# test: setups = diffraction, mono
# test: setupcode = SetDetectors(det)
# test: setupcode = maw(wavelength, 2.)

# Read all devices and try a count.

read()
count(1)
