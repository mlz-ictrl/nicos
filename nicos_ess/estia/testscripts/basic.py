# pylint: skip-file

# test: subdirs = v20
# test: setups = actuators
# test: needs = streaming_data_types

read()
status()

move(am1, 5)
move(am2, -5)
move(am3, 1)
wait(am1, am2, am3)
