# Default MIRA GUI config

from nicos.gui.panels import vsplit, hsplit, panel, window

default_profile_config = ('Default', [
    vsplit(
        hsplit(
            panel('nicos.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.gui.panels.watch.WatchPanel')),
        panel('nicos.gui.panels.console.ConsolePanel'),
        ),
    window('Errors/warnings', 'errors', True,
           panel('nicos.gui.panels.errors.ErrorPanel')),
    window('Editor', 'editor', False,
           panel('nicos.gui.panels.editor.EditorPanel')),
    window('Live data', 'live', True,
           panel('nicos.gui.panels.live.LiveDataPanel')),
    window('Analysis', 'plotter', True,
           panel('nicos.gui.panels.analysis.AnalysisPanel')),
    window('History', 'find', True,
           panel('nicos.gui.panels.history.HistoryPanel')),
    ], []
)
