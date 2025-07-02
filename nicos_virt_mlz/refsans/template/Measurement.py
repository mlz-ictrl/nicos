# scrtipt Sample

# SAMPLE NAMES
sample =  "Si/Ti/Al in air"

#PARAMETERS OF ALIGNMENT
top_z =  4.5
bg = 0.00 # backguard

# ANGLES
theta_val = [0.50, 2.50]
th_offset = 0.00 #will be substracted

# APERTURES
zb3_val = [0.92, 0.92, 4.60]
b3_val = [0.58, 0.58, 2.93]

# DETECTOR
yoke = [0.0 , 50.0, 1000.0]
table_val = 2500

# MESSZEITEN
mtime_pri = 600
mtime_low = 900
mtime_high = 1800

move(b1, [0.0, 12.0])
move(b2, [0.0, 12.0])
move(bs1, [0.0, 12.0])
move(zb0, 0.0)
move(zb1, 0.0)
move(zb2, 0.0)
move(h3, [0.0, 40.0])

# Set the optics, just in case
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

move(det_table,table_val)
move(gonio_top_z, top_z)

wait()

if mtime_pri > 0: # Check for the primary
    move(backguard, bg)
    move(zb3,[0, zb3_val[0]])
    move(b3,[0, b3_val[0]])
    move(gonio_theta, 0.00- th_offset)
    move(det_yoke,yoke[0])
    move(gonio_z, -4.0)
    wait(backguard, b1, zb3, gonio_theta, det_yoke, gonio_z)
    maw(shutter,'open')
    Remark('primary for %s' %(sample))
    count(mtime_pri)
    maw(shutter,'closed')

NewSample(sample)

if mtime_low > 0: # set elements for low angle
    move(backguard, bg)
    move(zb3,[0, zb3_val[1]])
    move(b3,[0, b3_val[2]])
    move(gonio_theta,theta_val[0]-th_offset)
    move(det_yoke,yoke[1])
    move(gonio_z, 0.0)
    wait(backguard, b1, b3, gonio_theta, det_yoke, gonio_z, nok5a, nok5b)
    maw(shutter,'open')
    Remark('reflectivity for %s at %.2f deg' %(sample,theta_val[0]))
    count(mtime_low)
    maw(shutter,'closed')

if mtime_high > 0: # set elements for high angle
    move(backguard, bg)
    move(zb3,[0, zb3_val[2]])
    move(b3,[0, b3_val[2]])
    move(gonio_theta,theta_val[1]-th_offset)
    move(det_yoke,yoke[2])
    move(gonio_z, 0.0)
    wait(backguard, b1, b3, gonio_theta, det_yoke, gonio_z, nok5a, nok5b)
    maw(shutter,'open')
    Remark('reflectivity for %s at %.2f deg' %(sample,theta_val[1]))
    count(mtime_high)
    maw(shutter,'closed')

print('measurements done')