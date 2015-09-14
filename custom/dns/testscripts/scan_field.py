# pylint: skip-file

# Typical sample-detector scan going through all field configurations.

N = 100
DET_CENTER = -15.0
SAMPLE_CENTER = 70.

m = field.mapping.keys()
m.remove("off")
m.remove("zero field")
for i in range(N):
    for f in m:
        cscan([det_rot, sample_rot], [DET_CENTER, SAMPLE_CENTER], [0.5, 0.2], 10,
              field=f, flipper=['on', 'off'], tsf=20, tnsf=10)
