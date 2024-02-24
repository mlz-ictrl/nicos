# pylint: skip-file

# test: needs = pika>=0.11.0
# test: setups = xresd
# test: subdirs = labs/physlab/xresd

read(hv, ctt, 'gen_voltage', 'gen_current', 'gen_ramp_dev', generator)
maw(ctt, 0)
