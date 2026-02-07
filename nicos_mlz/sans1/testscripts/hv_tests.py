# pylint: skip-file

# test: needs = tango
# test: setups = detector

wait_time = 300
maxofftime = det1_hv_offtime._attached_hv_supply.maxofftime / 3600

# Test case 0
det1_hv_offtime.reset()  # set cold state
assert int(det1_hv_offtime.read(0).split(':')[0]) >= maxofftime
assert det1_hv.read(0) == 'OFF'
for target in ('LOW', 'OFF'):
    maw(det1_hv, target)
    sleep(wait_time)

# Test case 1
det1_hv_offtime.reset()  # set cold state
assert int(det1_hv_offtime.read(0).split(':')[0]) >= maxofftime
assert det1_hv.read(0) == 'OFF'
for target in ('ON', 'LOW', 'ON', 'OFF'):
    maw(det1_hv, target)
    sleep(wait_time)

# Test case 2
assert int(det1_hv_offtime.read(0).split(':')[0]) < maxofftime
assert det1_hv.read(0) == 'OFF'
for target in ('LOW', 'OFF'):
    maw(det1_hv, target)
    sleep(wait_time)

# Test case 3
det1_hv_offtime.reset()  # set cold state
assert int(det1_hv_offtime.read(0).split(':')[0]) >= maxofftime
assert det1_hv.read(0) == 'OFF'
for target in ('LOW', 'ON', 'OFF'):
    maw(det1_hv, target)
    sleep(wait_time)
