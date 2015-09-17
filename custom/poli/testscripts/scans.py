# pylint: skip-file

# Typical continuous scans over several axes.

maw(twotheta, 32)
contscan(omega, 15, -165, 0.02, 7)
maw(chi2, 5.0)
contscan(omega, -165, 15, 0.02, 7)
maw(chi2, -5.0)

contscan(twotheta, 4, 40, 0.008, 25)
