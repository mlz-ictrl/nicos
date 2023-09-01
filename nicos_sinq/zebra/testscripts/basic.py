# pylint: skip-file

# test: needs = kafka
# test: needs = epics
# test: needs = streaming_data_types>=0.16.0
# test: needs = confluent_kafka
# test: subdirs = zebra
# test: setups = zebranb, wagen1, sps, detector_single

checkzebra()
zebraconf()
status()
Sample.a = 3.5
Sample.b = 3.5
Sample.c = 3.5
read()
