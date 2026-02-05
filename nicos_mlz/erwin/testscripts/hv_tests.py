# pylint: skip-file

# test: needs = tango,dataparser
# test: setups = charmbig

wait_time = 300

# Test case 0
b_hv_offtime.reset()  # set cold state
assert int(b_hv_offtime.read(0).split(':')[0]) >= 12
assert b_hv.read(0) == 'off'
for target in ('safe', 'off'):
    maw(b_hv, target)
    sleep(wait_time)

# Test case 1
b_hv_offtime.reset()  # set cold state
assert int(b_hv_offtime.read(0).split(':')[0]) >= 12
assert b_hv.read(0) == 'off'
for target in ('on', 'safe', 'on', 'off'):
    maw(b_hv, target)
    sleep(wait_time)

# Test case 2
assert int(b_hv_offtime.read(0).split(':')[0]) < 12
assert b_hv.read(0) == 'off'
for target in ('safe', 'off'):
    maw(b_hv, target)
    sleep(wait_time)

# Test case 3
b_hv_offtime.reset()  # set cold state
assert int(b_hv_offtime.read(0).split(':')[0]) >= 12
assert b_hv.read(0) == 'off'
for target in ('safe', 'on', 'off'):
    maw(b_hv, target)
    sleep(wait_time)
