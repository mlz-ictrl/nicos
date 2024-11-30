# pylint: skip-file

# test: subdirs = nido
# test: setups = area_detectors,forwarder,rotation_stage
# test: needs = p4p
# test: needs = streaming_data_types
# test: needs = confluent_kafka
# test: needs = yuos_query

read()
status()

SetDetectors('area_detector_collector')

hama_image_type.move(3)
hama_image_type.move(0)

scan(rotation_stage, 0, 720, 101, hama_camera=10)

scan(rotation_stage, 0, 720, 101, hama_camera=1)
