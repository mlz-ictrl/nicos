# pylint: skip-file

# test: needs = epics,lxml
# test: needs = streaming_data_types>=0.16.0
# test: needs = confluent_kafka
# test: subdirs = camea
# test: setups = cameabasic, detector
# test: setupcode = SetDetectors(cameadet)

moveCAMEA(s2t=-35)
prepareCAMEA()
CAMEAscan([5,5.13],  s2ts=[-40], a3Start=0, a3Stepsize=1, a3Steps=181,
          m=100000, skipScans=0)
moves2tPeak([1, 0, 0])
