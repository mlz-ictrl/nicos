# pylint: skip-file

# test: subdirs = frm2
# test: setups = pgaa
# test: setupcode = SetDetectors(_60p, LEGe)
# test: setupcode = maw(att, 100)
# test: setupcode = maw(shutter, 'closed')

# read some basic devices

read(shutter)
read(att1)
read(att2)
read(att3)

read(chamber_pressure)
status(chamber_pressure)
LEGe.status(0)

read(Sample)

maw(shutter, 'open')
maw(shutter, 'closed')
count(TrueTime=1)
