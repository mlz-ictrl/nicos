# pylint: skip-file

# test: needs = nicos.devices.vendor.caress.CARESS
# test: subdirs = frm2
# test: subdirs = spodi
# test: setups = spodi
# test: setupcode = SetDetectors(adet)
# test: setupcode = tthm.maw(155)

read()
status()
adet.resosteps = 40
tths.precision = 0.001
count(1)
count(1, resosteps=5)
for angle in [0, 2, 4]:
    maw(tths, angle)
    count(t=1)
scan(tths, [0, 2, 4], resosteps=2, t=1)
