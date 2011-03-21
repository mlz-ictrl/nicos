import socket, struct, time
import numpy

x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
x.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
x.bind(('localhost', 1234))
x.listen(1)
ts = 0

ram = numpy.ones(128 * 128, '<I4')
rnd = numpy.random.poisson(200, 128 * 128)

#ram = 'IMAG' + ''.join((chr(i) + '\x00\x00\x00') * 128 for i in range(128))
while True:
    try:
        conn, addr = x.accept()
        print 'got connection'
        while True:
            length = conn.recv(4)
            l, = struct.unpack('i', length)
            cmd = conn.recv(l)
            print 'got cmd:', cmd
            if cmd.startswith('CMD_config'):
                mt = float(dict(v.split('=') for v in cmd[10:-1].split())['time'])
                resp = 'OKAY'
            elif cmd.startswith('CMD_start'):
                ts = time.time()
                resp = 'OKAY'
            elif cmd.startswith('CMD_status'):
                resp = 'ERR_stop=%d' % bool(time.time() > ts+mt)
            elif cmd.startswith('CMD_readsram'):
                resp = 'IMAG' + (rnd * int(time.time()-ts) * ram).tostring()
#                print len(resp)
            else:
                resp = 'ERR_unknown command'
            length = struct.pack('i', len(resp))
            conn.send(length + resp)
    except Exception, e:
        print 'EXCEPTION:', e 
    
