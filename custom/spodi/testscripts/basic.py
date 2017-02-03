# pylint: skip-file

# test: subdirs = frm2
# test: setups = spodi
# test: setupcode = SetDetectors(det)

read()
adet.resosteps = 40
tths.precision = 0.001
count(1)
count(1, resosteps=5)
for angle in [0, 2, 4]:
    maw(tths, angle)
    count(t=1)
scan(tths, [0, 2, 4], resosteps=2, t=1)
