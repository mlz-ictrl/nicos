"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
     panel('nicos.clients.gui.panels.generic.GenericPanel',
           uifile='custom/demo/lib/gui/piface.ui'),
    )
)

windows = [
]

tools = [
]
