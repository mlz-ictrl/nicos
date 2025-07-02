# Script to scan gonio_z. The sample is 50x80 mm2. For a configuration vc:nok8, slit optizer gives the following apertures:
#
# Angle             0.5deg          2.5deg
#
# zb3               0.92 mm         4.60 mm
# b3                0.58 mm         2.93 mm
#
# for a 7% angular resolution and 55 mm distance between b3 and the sample

# Define the sample and its properties
d_last_slit_sample.move(55.0)
Sample.length = 80.0
Sample.width = 50.0
move(gonio_z, 0.0)
move(gonio_top_z, 3.5)

move(zb3, (0.0, 0.92))
move(b3, (0.0, 0.58))

# Move all the motors for the alignment to null. We assume the sample aligned, except for the vertical position
move(gonio_phi, 0.0)
move(gonio_omega, 0.0)
move(gonio_y, 0.0)
move(gonio_z, 0.0)
move(gonio_top_phi, 0.0)
move(gonio_top_theta, 0.0)
move(backguard, 0.0)
move(gonio_top_z, 3.5) # Initial position

# We tilt the sample and scan gonio_top_z
move(gonio_theta, 0.5)
wait()
scan(gonio_top_z, 3.5, 0.1, 25, t = 10)






