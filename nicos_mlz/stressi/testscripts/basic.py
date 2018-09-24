# pylint: skip-file

# test: needs = CARESS
# test: subdirs = frm2
# test: setups = stressi
# test: setupcode = SetDetectors(adet)

read()
status()
count(t=1)
scan(xt, 0, 1, 5, t=1)
scan(xt, 0, 1, 5, 'test', t=1)
timescan(1, t=1)
timescan(1, 'test', t=1)
