# pylint: skip-file

# test: subdirs = frm2
# test: setups = bruker-axs,detectors
# test: setupcode = SetDetectors(pilatus)

# conditioning and count with pilatus

tubecond.calibrate(30)
SetDetectors(pilatus)
count(1000, t=5)
