# pylint: skip-file

# Typical sample-detector scan with different fields per point.

N = 100
DET_CENTER = -10.0
SAMPLE_CENTER = 100.0

for i in range(N):
    cscan([det_rot, sample_rot], [DET_CENTER, SAMPLE_CENTER], [0.5, 2],
          10, field=['x7_sf', 'x7_nsf', 'y7_sf', 'y7_nsf', 'z7_sf', 'z7_nsf'], tsf=60, tnsf=60)
