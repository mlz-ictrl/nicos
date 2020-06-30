main_window = docked(
    tabbed(
        (
            "Setup",
            tabbed(
                ("Experiment", panel("nicos_ess.gui.panels.setup_panel.ExpPanel")),
                ("Instrument", panel("nicos_ess.gui.panels.setup_panel.SetupsPanel")),
            ),
        ),
        (
            "Samples",
            vsplit(panel("nicos_ess.loki.gui.sampleconf.KWSSamplePanel")),  # vsplit
        ),
        ("  ", panel("nicos_ess.gui.panels.empty.EmptyPanel")),
        (
            "Instrument interaction",
            hsplit(
                vbox(
                    panel(
                        "nicos_ess.gui.panels.cmdbuilder.CommandPanel",
                        modules=["nicos.clients.gui.cmdlets"],
                    ),
                    tabbed(
                        (
                            "Output",
                            panel(
                                "nicos_ess.gui.panels.console.ConsolePanel",
                                hasinput=False,
                            ),
                        ),
                        ("Scan Plot", panel("nicos_ess.gui.panels.scans.ScansPanel")),
                        (
                            "Detector Image",
                            panel("nicos_ess.gui.panels.live.LiveDataPanel"),
                        ),
                        (
                            "Script Status",
                            panel(
                                "nicos_ess.gui.panels.status.ScriptStatusPanel",
                                eta=True,
                            ),
                        ),
                    ),
                ),  # vsplit
                panel(
                    "nicos_ess.gui.panels.devices.DevicesPanel",
                    dockpos="right",
                    param_display={"tas": "scanmode", "Exp": ["lastpoint", "lastscan"]},
                    filters=[("Detector", "det"), ("Temperatures", "^T"),],
                ),
            ),  # hsplit
        ),
        (
            "Script Editor",
            vsplit(
                panel(
                    "nicos.clients.gui.panels.scriptbuilder.CommandsPanel",
                    modules=["nicos_mlz.kws2.gui.cmdlets"],
                ),
                panel(
                    "nicos.clients.gui.panels.editor.EditorPanel",
                    tools=[
                        tool("Scan Generator", "nicos.clients.gui.tools.scan.ScanTool")
                    ],
                ),
            ),
        ),
        ("Detector Image", panel("nicos_ess.gui.panels.live.LiveDataPanel")),
        ("History", panel("nicos_ess.gui.panels.history.HistoryPanel"),),
        (
            "Logs",
            tabbed(
                ("Errors", panel("nicos.clients.gui.panels.errors.ErrorPanel")),
                (
                    "Log files",
                    panel("nicos.clients.gui.panels.logviewer.LogViewerPanel"),
                ),
            ),
        ),
        ("  ", panel("nicos_ess.gui.panels.empty.EmptyPanel")),
        ("Finish Experiment", panel("nicos_ess.gui.panels.setup_panel.FinishPanel")),
        position="left",
    ),  # tabbed
)  # docked

windows = []

tools = [
    tool(
        "Report NICOS bug or request enhancement",
        "nicos.clients.gui.tools.bugreport.BugreportTool",
    ),
]

options = {
    "ess_gui": True,
}
