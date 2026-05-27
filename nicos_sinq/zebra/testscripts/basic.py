# pylint: skip-file

# test: needs = epics,lxml
# test: needs = streaming_data_types>=0.16.0
# test: needs = confluent_kafka
# test: subdirs = zebra
# test: setups = zebranb, wagen1, sps, detector_single
# test: setupcode = Sample.a=3.5
# test: setupcode = Sample.b=3.5
# test: setupcode = Sample.c=3.5
# test: setupcode = maw(zebramode, 'nb')
# test: setupcode = ublist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'NU'),())
# test: setupcode = messlist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'NU'),())
# test: setupcode = satref.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'NU'),())
# test: setupcode = maw(chi, 180, phi, 0)

# checkzebra() The SPS Device has been temporarily removed
# zebraconf()
status()
assert chi.read(0) == 180
assert phi.read(0) == 0
Sample.a = 3.5
Sample.b = 3.5
Sample.c = 3.5
read()
