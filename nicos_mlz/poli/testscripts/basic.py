# pylint: skip-file

# test: subdirs = poli
# test: setups = diffraction
# test: setups = mono
# test: setupcode = SetDetectors(det)
# test: setupcode = maw(wavelength, 2.)

# Read all devices and try a count.

read()
count(1)
