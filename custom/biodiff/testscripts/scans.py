# -*- coding: utf-8 -*-
# pylint: skip-file

# BioDiff has to be in the following setup:
#
# - Imageplate hochgefahren
# - Raumtemperatureinsatz drin,
# - Tieftemperatureinsatz angeschlossen, aber in Ständer
#   neben dem Instrument.
# - Both detectors are switched on

NewSetup("ccd")
rscan(omega_samplestepper_m, 0.0, 0.3, 1.0, t=1200)
rscan(omega_sampletable_m, 90.0, 0.5, 92.0, t=3600)
scan(omega_samplestepper, 5.0, 0.2, 5, t=600)
count(0.5)
count(200)

NewSetup("imageplate")
rscan(omega_samplestepper_m, 0.0, 0.3, 1.0, t=1200)
rscan(omega_sampletable_m, 90.0, 0.5, 92.0, t=3600)
scan(omega_samplestepper, 5.0, 0.2, 5, t=600)
count(200)
