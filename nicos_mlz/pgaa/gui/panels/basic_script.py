# PGAA specific script
# pylint: skip-file

start, _wait = __start__
wa = start - currenttime()

if wa + _wait < 2:
    sleep(2)
elif wa <= _wait:
    sleep(_wait)
else:
    sleep(wa + _wait)

SetDetectors(*__Detectors__)
NewSample('__Name__')

sc.move(__Pos__)
att.move(__Attenuator__)
ellcol.move('__ElCol__')
wait(sc, att, ellcol)
for d in Exp.detectors:
    d.enablevalues = ['__Beam__']
push.move('down')
wait(push)
count('__Comment__', Filename='__Suffix__', __stop_by__=__at_after__)
push.maw('up')
sleep(1)
