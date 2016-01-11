"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
     panel('generic.GenericPanel', uifile='custom/demo/lib/gui/piface.ui'),
    )
)

windows = [
]

tools = [
]
