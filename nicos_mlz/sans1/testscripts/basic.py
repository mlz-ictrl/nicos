# pylint: skip-file

# test: subdirs = frm2
# test: setups = sans1, selector042
# test: setupcode = SetDetectors(det1)
# test: needs = PIL

# test selector
maw(selector_rpm, 21230)
maw(selector_rpm, 3100)
maw(selector_lambda, 6)
maw(selector_lambda, 12)

# test collimation
maw(att, 'x1000')
maw(att, 'x100')

maw(ng_pol, 'pol1')
maw(ng_pol, 'ng')

# These test cases disabled due to problems with 'instrument_shutter' device
# maw(col, 20)
# maw(col, 2)

maw(bg1, '41mm')
maw(bg1, 'open')

maw(bg2, '19mm')
maw(bg2, 'open')

maw(sa1, '9mm')
maw(sa1, '29mm')

maw(sa2, 8)

# test Huber tower
maw(st_x, -200)
maw(st_z, 10)
maw(st_y, 10)
maw(st_phi, 5)
maw(st_chi, 5)
maw(st_omg, 5)
maw(st_x, 0)
maw(st_z, 0)
maw(st_y, 0)
maw(st_phi, 0)
maw(st_chi, 0)
maw(st_omg, 0)

# test detector
maw(det1_hv, 'ON')
maw(det1_hv, 'OFF')
maw(det1_x, 550)
maw(det1_x, 4)
maw(det1_z, 20000)

# High voltage auto shutdown test
maw(det1_z, 4000)
maw(det1_hv, 'ON')
maw(det1_z, 20000)

# Test laser
maw('laser', 'On')
read('laser')
maw('laser', 'Off')
read('laser')
maw('laser', 1)
read('laser')
maw('laser', 0)
read('laser')
