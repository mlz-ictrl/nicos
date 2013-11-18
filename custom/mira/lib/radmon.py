import subprocess
from urllib2 import HTTPBasicAuthHandler, build_opener

from nicos.core import Readable, NicosError, status

class RadMon(Readable):

    def doInit(self, mode):
        h = HTTPBasicAuthHandler()
        h.add_password(realm='Administrator or User', uri='http://miracam.mira.frm2/IMAGE.JPG',
                       user='rgeorgii', passwd='rg.frm2')
        self._op = build_opener(h)

    def doRead(self, maxage=0):
        img = self._op.open('http://miracam.mira.frm2/IMAGE.JPG').read()
        open('/tmp/radmon.jpg', 'wb').write(img)
        p1 = subprocess.Popen('/usr/local/bin/ssocr -d 3 -i 2 -t 40 rotate 268 crop 298 192 55 34 '
                              'make_mono invert opening 1 /tmp/radmon.jpg'.split(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen('/usr/local/bin/ssocr -d 1 -i 2 -t 40 rotate 268 crop 387 158 23 30 '
                              'make_mono invert opening 1 /tmp/radmon.jpg'.split(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out1, err1 = p1.communicate()
        out2, err2 = p2.communicate()
        out1 = out1.strip()
        out2 = out2.strip()
        if err1:
            raise NicosError(self, 'ERROR in mantissa')
        if err2:
            raise NicosError(self, 'ERROR in exponent')
        return 0.01 * float(out1 + 'e-' + out2) * 1e6  # convert to uSv/h

    def doStatus(self, maxage=0):
        return status.OK, ''
