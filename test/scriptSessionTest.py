from nicos.sessions.simple import ScriptSession
from nicos.utils import loggers
from os import path
import logging
import os

class ScriptSessionTest(ScriptSession):
    def __init__(self, appname):
        ScriptSession.__init__(self, appname)
        self.setSetupPath(path.join(path.dirname(__file__), 'setups'))

    def createRootLogger(self, prefix='nicos'):
        self.log = loggers.NicosLogger('nicos')
        self.log.parent = None
        # show errors on the console
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(
            logging.Formatter('[SCRIPT] %(name)s: %(message)s'))
        self.log.addHandler(handler)
        log_path = path.join(path.dirname(__file__),'root','log')
        try:
            if prefix == 'nicos':
                self.log.addHandler(loggers.NicosLogfileHandler(
                    log_path, 'nicos', str(os.getpid())))
                # handler for master session only
                self._master_handler = loggers.NicosLogfileHandler(log_path)
                self._master_handler.disabled = True
                self.log.addHandler(self._master_handler)
            else:
                self.log.addHandler(loggers.NicosLogfileHandler(log_path, prefix))
                self._master_handler = None
        except (IOError, OSError), err:
            self.log.error('cannot open log file: %s' % err)
