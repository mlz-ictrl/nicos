# pylint: skip-file

# test: needs = tango
# test: subdirs = frm2
# test: setups = mieze

move(selector_lambda, 6.0)
move(cbox_0a_fg_freq, 4500, cbox_0b_fg_freq, 6200)
move(hrf_0a, 0.114293, hrf_0b, 0.157471, nse0, 0)
move(stx, 0, sty, 0, stz, 0, sgx, 0, sgy, 0, srz, 0)
move(arm2_rot, 0.0)
move(gf0, 0, gf1, 0, gf2, 0,
     # gf3, 0,
     gf4, 0, gf5, 0, gf6, 0, gf7, 0, gf8, 0, gf9, 0, gf10, 0)
wait()

read(echotime)
