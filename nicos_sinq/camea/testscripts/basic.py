# pylint: skip-file

# test: needs = epics
# test: needs = streaming_data_types>=0.16.0
# test: needs = confluent_kafka
# test: subdirs = camea
# test: setups = cameabasic, detector
# test: setupcode = SetDetectors(cameadet)

read()
status()
maw(a4, 2)
maw(mono, 3)
timescan(1, t=1)
