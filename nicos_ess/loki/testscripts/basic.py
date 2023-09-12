# pylint: skip-file

# test: subdirs = loki
# test: setups = aperture,beamstop,chopper_1,chopper_2,collimator_1,collimator_2,detectors,gate_valve,laser,monitors,shutters,slit_set_1,slit_set_2,slit_set_3
# test: needs = streaming_data_types
# test: needs = confluent_kafka
# test: needs = yuos_query

read()
status()
