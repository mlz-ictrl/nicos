"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
     panel('nicos.clients.gui.panels.generic.GenericPanel',
           uifile='custom/pgaa/lib/gui/shutter.ui'),
    )
)

windows = [
]

tools = [
]
