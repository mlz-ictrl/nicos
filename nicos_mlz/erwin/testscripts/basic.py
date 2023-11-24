# pylint: skip-file

# test: setups = detector, charmsmall

read()
status()
for v in ['on', 'safe', 'off']:
    maw(s_hv, v)
stop(s_hv)
reset(s_hv)
