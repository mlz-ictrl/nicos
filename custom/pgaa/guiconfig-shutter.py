"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
     panel('generic.GenericPanel', uifile='custom/pgaa/lib/gui/shutter.ui'),
    )
)

windows = [
]

tools = [
]
