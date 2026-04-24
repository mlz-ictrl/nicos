# pylint: skip-file

# test: needs = epics,lxml
# test: needs = streaming_data_types>=0.16.0
# test: needs = confluent_kafka
# test: subdirs = focus
# test: setups = focus, detector

read()
status()
read(wavelength)
maw(wavelength, 2.5)
assert mth.precision == 0.2
assert mtt.precision == 0.2
