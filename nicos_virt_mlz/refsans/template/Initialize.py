# Script to setup the instrument (initialization procedure)
NewSetup('refsans')
alphai.alias = 'gonio_theta'
d_last_slit_sample.alias = 'sample_x_manual'
last_aperture.alias = 'b3.opening'
primary_aperture.alias = 'zb3.opening'

move(chopper, {'wlmin': 2.0, 'wlmax': 21.0, 'gap': 0.1, 'chopper2_pos': 5, 'D': 15.6496, 'manner': 'normal'})
det_table.move(2500.0)
det_yoke.move(0.0)
#det_pivot.move(9)
move(optic, 'horizontal')
move(det_drift, 'drift2')

# Set the optics to vc:nok8. Leider darf nok5a NICHT in der richtigen (vc) Position bewegt werden. Es gibt einen Bug in der
# Verbindung zwischen der McStas-REFSANS-Datei und NICOS, der korrigiert werden muss.
nok5a.mode = 'ng'
nok5b.mode = 'ng'
nok6.mode = 'ng'
nok7.mode = 'ng'
nok8.mode = 'vc'
nok9.mode = 'vc'
sleep(30)

move(nok5a, [0.0, 0.0])
move(nok5b, [0.0, 0.0])
move(nok6, [0.0, 0.0])
move(nok7, [0.0, 0.0])
move(nok8, [37.5, 37.5])
move(nok9, [37.5, 37.5])

#Set the slits to a fully opened configuration
move(b1, (0.0, 12.0))
move(zb0, 0.0)
move(zb1, 0.0)
move(zb2, 0.0)
move(zb3, (0.0, 12.0))
move(bs1, (0.0, 12.0))
move(b2, (0.0, 12.0))
move(b3, (0.0, 12.0))
move(h3, (0.0, 40.0))

move(gonio_z, -10.0)
move(gonio_top_z, 0.0)

# Test for a short measurement (direct beam)
wait()
count(10)




