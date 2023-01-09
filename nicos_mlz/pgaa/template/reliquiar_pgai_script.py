# Reliquiar Mainz PGAI
# attention, due to the roation from 45 to 225 deg, D2C1 is in reality D2C4

# detector preferences
detector_type = [_60p]
time_value = 10800

# beam preferences
shutter_action = 'open'  # 'closed'
atten_value = 100
collimator = 'Col'  # 'Ell'

# savefile infos
sample_name = 'EK_Reliq'

w_value = [225]    # 45deg for D1

# x and y coordinates
col_4 = (88.47, 73.77)    # col_1 = (88.47, 73.77) for D1 45deg
col_3 = (96.97, 82.27)    # col_2 = (96.97, 82.27) for D1 45deg
col_2 = (105.47, 90.77)   # col_3 = (105.47, 90.77) for D1 45deg
col_1 = (113.97, 99.27)   # col_4 = (113.97, 99.27) for D1 45deg
columns = [col_1, col_2, col_3, col_4]

# z coordinates
rows = (45.31, 53.60, 61.89, 70.18, 78.47, 86.76)


def take_pgaa(xt, yt, zt, w, shutter_action, col, row, t=2):
    print('recording %.2f and %.2f and %.2f' % (xt, yt, zt))
    info_string = 'D%dC%dR%d' % (t, col, row)
    file_string = '_x_%.2f_y_%.2f_z_%.2f_w_%.0f' % (xt, yt, zt, w)
    x.move(xt)
    y.move(yt)
    z.move(zt)
    wait(x, y, z)
    shutter.maw(shutter_action)
    count(info_string, LiveTime=time_value, Filename=file_string)
    shutter.maw('closed')
    print('spectra recorded and written to %s' % file_string)

SetDetectors(*detector_type)
NewSample(sample_name)
att.maw(atten_value)
ellcol.maw(collimator)

for _c, col in enumerate(columns):
    if _c in [0, 3]:
        _rows = rows[2:4]
        _roff = 3
    elif _c in [1, 2]:
        _rows = rows
        _roff = 1
    else:
        continue
    _x, _y = col
    for _r, _z in enumerate(_rows):
        take_pgaa(_x, _y, _z, w_value[0], shutter_action, _c + 1, _r + _roff)

# scan 1 special position at Reliquiar-sealing's center
# coordinates
x_value = 98.72
y_value = 89.07
z_value = 37.02

take_pgaa(x_value, y_value, z_value, w_value[0], shutter_action, 5, 1, t=1)
