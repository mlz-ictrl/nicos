from nicos import session
from nicos.commands import usercommand
from nicos.core.constants import SIMULATION


@usercommand
def start_filewriter():
    """
    A hacky way of starting the NeXus Filewriter.
    """
    if session.mode == SIMULATION:
        session.log.info('=> dry run: starting file writing')
    else:
        point = session.experiment.data.beginPoint()
        sink = session.getDevice('NexusDataSink')
        point.handlers = [sink.handlerclass(sink, point, None)]
        point.dispatch('prepare')
        point.dispatch('begin')


@usercommand
def stop_filewriter():
    """
    A hacky way of stopping the NeXus Filewriter.
    """
    if session.mode == SIMULATION:
        session.log.info('=> dry run: stopping file writing')
    else:
        session.experiment.data.finishPoint()
