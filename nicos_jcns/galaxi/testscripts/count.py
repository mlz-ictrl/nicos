# pylint: skip-file

# test: subdirs = frm2
# test: setups = bruker_axs,pilatus_det
# test: setupcode = SetDetectors(pilatus)
# test: skip

# conditioning and count with pilatus

tubecond.calibrate(30)
SetDetectors(pilatus)
count(1000, t=5)
