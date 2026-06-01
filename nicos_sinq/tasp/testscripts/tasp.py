# pylint: skip-file

# test: needs = epics
# test: needs = streaming_data_types>=0.16.0
# test: needs = confluent_kafka
# test: subdirs = tasp
# test: setups = tasp
# test: setupcode = SetDetectors(taspdet)
# test: setupcode = DAQPreset.monitor_channel = 'monitor2'
# test: setupcode = move(ThresholdChannel, 'monitor2')
# test: setupcode = move(Threshold, 200)

read()
status()
cscan(a4, 93.63, 0.15, 11, m=100000)
