# pylint: skip-file

# test: skip
# test: subdirs = laue
# test: setups = kappa

# basic scan:

for x in range(-10,10,1):
    maw(stx,x)
    count(10)
