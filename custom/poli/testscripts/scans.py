# pylint: skip-file

# Typical continuous scans over several axes.

maw(gamma, 32)
contscan(omega, 15, -165, 0.02, 7)
maw(chi2, 5.0)
contscan(omega, -165, 15, 0.02, 7)
maw(chi2, -5.0)

contscan(gamma, 4, 40, 0.008, 25)
