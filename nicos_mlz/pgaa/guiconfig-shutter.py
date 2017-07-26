"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
     panel('nicos.clients.gui.panels.generic.GenericPanel',
           uifile='nicos_mlz/pgaa/gui/shutter.ui'),
    )
)

windows = [
]

tools = [
]
