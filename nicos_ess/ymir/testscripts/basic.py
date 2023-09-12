# pylint: skip-file

# test: subdirs = ymir
# test: setups = alignment_stack,choppers,event_receiver,forwarder,huginn_sans,huginn_subcryo,julabo_f25,just-bin-it,lakeshore336,laser_detector,macgyver_analog_in,macgyver_analog_out,macgyver_digital_in,macgyver_digital_out,macgyver_relay,macgyver_temperature,readout_master,syringe_pump_ne1600
# test: needs = streaming_data_types
# test: needs = confluent_kafka
# test: needs = yuos_query

read()
status()

SetDetectors('laser')

scan(mY, 10, 20, 11)
