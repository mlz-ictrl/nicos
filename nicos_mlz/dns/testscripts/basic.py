# pylint: skip-file

# test: needs = tango
# test: setups = dns, dnsplotfiles
# test: setupcode = SetDetectors(det)

# Read all devices and try a count.

read()
status()
count(10)
