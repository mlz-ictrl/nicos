# pylint: skip-file

# test: setups = detsmall
# test: setups = charmsmall

read()
status()
for v in ['on', 'safe', 'off']:
    maw(s_hv, v)
stop(s_hv)
reset(s_hv)
