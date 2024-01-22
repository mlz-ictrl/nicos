# pylint: skip-file

# test: needs = kafka
# test: needs = epics
# test: needs = streaming_data_types>=0.16.0
# test: needs = confluent_kafka
# test: subdirs = morpheus
# test: setups = diffraction

# read all device values and statuses
read()
status()

# test the AldiMotor
d1t.startBack()
maw(d1t, 10)
d1t.startBack()
maw(d1t, 0)
d1t.startBack()
maw(slit1_width, 10)
maw(slit1_width, 0)

# test special command
ScanOmega((0, 0, 0))
move(slit1_width, 0)
move(slit1_width, 10)
