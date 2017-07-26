# pylint: skip-file

# test selector
maw(selector_rpm, 21230)
maw(selector_rpm, 3100)
maw(selector_lambda, 6)
maw(selector_lambda, 12)

# test collimation
maw(att, 'x1000')
maw(att, 'x100')

maw(ng_pol, 'las')
maw(ng_pol, 'ng')

maw(col, 20)
maw(col, 2)

maw(bg1, '42mm')
maw(bg1, 'open')

maw(bg2, '20mm')
maw(bg2, 'open')

maw(sa1, '50x50')
maw(sa1, '10mm')

maw(sa2, 8)

# test Huber tower
maw(st1_x, -200)
maw(st1_z, 10)
maw(st1_y, 10)
maw(st1_phi, 5)
maw(st1_chi, 5)
maw(st1_omg, 5)
maw(st1_x, 0)
maw(st1_z, 0)
maw(st1_y, 0)
maw(st1_phi, 0)
maw(st1_chi, 0)
maw(st1_omg, 0)

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
