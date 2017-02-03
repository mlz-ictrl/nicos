# pylint: skip-file

# test: subdirs = frm2
# test: setups = robot
# test: setupcode = SetDetectors(det)

# robot testing script

from nicos import session
read()
scan(tths, 30, 9, 9, 'test', t=1)
timescan(1, 'V_pin', t=1)
if 'robot' in session.loaded_setups:
    change_sample(0, 1)
    pole_figure(6, 0.12, 21, 'test')
