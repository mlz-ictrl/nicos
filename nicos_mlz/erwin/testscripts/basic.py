# pylint: skip-file

# test: setups = detsmall, charmsmall

read()
status()
for v in ['on', 'safe', 'off']:
    maw(s_hv, v)
stop(s_hv)
reset(s_hv)
