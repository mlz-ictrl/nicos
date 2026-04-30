# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import os
import re
import sys
import textwrap

import yaml

try:
    import orsopy
    # pylint: disable=import-error
    from orsopy.fileio import ComplexValue, Value, model_language as ml

except ModuleNotFoundError:
    orsopy = None

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QByteArray, QColor, QDialog, QEvent, \
    QFileDialog, QFont, QObject, QPlainTextEdit, QPushButton, QSize, \
    QSizePolicy, QSplitter, QSvgWidget, QSyntaxHighlighter, Qt, QTextBrowser, \
    QTextCharFormat, QTextEdit, QThread, QVBoxLayout, pyqtSignal, pyqtSlot
from nicos.utils import LOCALE_ENCODING, findResource

DEFAULT_SHAPE = 'None'
DEFAULT_MODEL = 'stack:'

class SampleViewer(QSvgWidget):
    """
    This class creates a schematic representation of the sample. It has been
    taken verbatim from
    https://github.com/reflectivity/orso_tools/blob/master/orso_tools/sample_viewer.py.

    The reason this class is not simply imported from orso_tools is that it is
    based on PySide6 in orso_tools, which could clash with the NICOS Qt version.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    COLORS = ["#ffaaaa", "#aaffaa", "#aaaaff", "#ff00ff", "#00ffff"]

    def sizeHint(self):
        return QSize(400, 300)

    def show_outdated(self):
        svg = """<svg width="100" height="100" viewbox="0 0 100 100"
                    xmlns="http://www.w3.org/2000/svg"> <text x="50" y="8"
                    fill="black" font-size="6" text-anchor="middle">Click "visualize" to draw the model</text>
        </svg>"""
        self.renderer().load(QByteArray(svg.encode("utf-8")))
        self.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

    def show_cannot_visualize(self):
        svg = """<svg width="100" height="100" viewbox="0 0 100 100"
                    xmlns="http://www.w3.org/2000/svg"> <text x="50" y="8"
                    fill="black" font-size="6" text-anchor="middle">Cannot visualize model</text>
        </svg>"""
        self.renderer().load(QByteArray(svg.encode("utf-8")))
        self.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

    def show_sample_model(self, model: "ml.SampleModel"):
        items = model.resolve_stack()

        _, height, svg_inside = self.build_substack(10, 10, 0, items)

        svg = f"""<svg width="100" height="{height}" viewbox="0 0 {height} 100"
        xmlns="http://www.w3.org/2000/svg"> <text x="50" y="8" fill="black"
        font-size="6" text-anchor="middle">Sample Model:</text>
        {svg_inside}
        </svg>"""
        self.renderer().load(QByteArray(svg.encode("utf-8")))
        self.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

    def build_substack(self, pos, height, indent, items):
        svg_inside = ""
        for item in items:
            if isinstance(item, ml.Layer):
                width = 100 - 5 - indent * 1.2
                svg_inside += f"""
                <rect width="{width}" height="18" x="{indent + 5}"
                y="{pos + 1}" rx="2" ry="2" fill="#cccccc" />
                <text x="{indent + 10}" y="{pos + 8}" fill="black"
                font-size="4">Layer {item.original_name or ''}</text>
                <text x="{indent + 20}" y="{pos + 13}" fill="black"
                font-size="3">
                thickness={item.thickness.magnitude} {item.thickness.unit}
                | roughness={item.roughness.magnitude} {item.roughness.unit}
                </text>"""
                pos += 20
                height += 20
            elif isinstance(item, ml.SubStack):
                new_pos, new_height, svg_substack = self.build_substack(pos + 7, height + 8, indent + 5, item.sequence)
                width = 100 - 5 - indent * 1.1
                pre_str = ""
                post_str = ""
                if item.repetitions != 1:
                    pre_str = f"{item.repetitions} X "
                if getattr(item, "environment", None) is not None:
                    post_str = f" in {item.environment.original_name or repr(item.environment)}"

                svg_inside += f"""
                <rect width="{width}" height="{new_height - height}"
                x="{indent + 5}" y="{pos}" rx="2" ry="2"
                fill="{self.COLORS[(indent // 5) % len(self.COLORS)]}" />
                <text x="{indent + 10}" y="{pos + 6}" fill="black" font-size="4">
                {pre_str}SubStack {item.original_name or ''}{post_str}
                </text>"""

                svg_inside += svg_substack
                pos = new_pos + 1
                height = new_height
            elif isinstance(item, ml.SubStackType):
                width = 100 - 5 - indent * 1.2
                parameter_text = ""
                param_height = 0
                for param, _ in item.to_dict().items():
                    if param in ["sub_stack_class", "original_name"]:
                        continue
                    obj = getattr(item, param)
                    value_str = repr(obj)
                    if isinstance(obj, Value):
                        value_str = f"{obj.magnitude} {obj.unit}"
                    elif isinstance(obj, ComplexValue):
                        value_str = f"{obj.real}+{obj.imag}i {obj.unit}"
                    elif isinstance(obj, ml.Material):
                        value_str = getattr(obj, "original_name", obj.formula)
                    parameter_text += f"""
                    <text x="{indent + 12}" y="{pos + 13 + param_height}"
                    fill="black" font-size="3">{param}={value_str}</text>"""
                    param_height += 3
                svg_inside += f"""
                <rect width="{width}" height="{10 + param_height}"
                x="{indent + 5}" y="{pos + 1}" rx="2" ry="2" fill="#ffffaa" />
                <text x="{indent + 10}" y="{pos + 8}" fill="black" font-size="4">
                    {item.__class__.__name__} {item.original_name or ''}
                </text>"""
                svg_inside += parameter_text
                pos += 12 + param_height
                height += 12 + param_height

        return pos, height, svg_inside

class HelpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orso model help")

        layout = QVBoxLayout()

        text = QTextBrowser()
        text.setReadOnly(True)

        html = textwrap.dedent("""
        <h1>The ORSO sample model language</h1>

        <p>
        <a href="https://www.reflectometry.org/advanced_and_expert_level/file_format/simple_model">Full documentation</a><br>
        <a href="https://www.reflectometry.org/advanced_and_expert_level/file_format/simple_model#examples">Examples</a><br>
        <a href="https://slddb.esss.dk/slddb/sample">ORSO sample builder</a><br>
        try local installation of the ORSO sample builder: > osb
        </p>

        <h2>The stack: a one-line description</h2>

        <pre>
        stack: vacuum | 5( Fe 4 | Si 3 ) | SiO2
        </pre>

        <ul>
        <li>The <i>outer</i> surface is on the left</li>
        <li>| symbolizes an interface</li>
        <li>Materials, layers and the like are marked with strings starting with a letter</li>
        <li>Layer thicknesses are given in nm</li>
        <li>Repetitions are marked by &lt;number&gt;(...)</li>
        </ul>

        <h2>More precise materials definition</h2>

        <pre>
        stack: vacuum | 5( Fe 4.2 | Si 3 ) | SiO2
        materials:
          Fe:
            magnetic_moment: 2.2
            relative_density: 0.95
        </pre>

        Available keys for a material:

        <pre>
        formula:          # [str]
        mass_density:     # / g cm^-3
        number_density:   # / nm^-3
        sld:              # / angstrom^-2
        magnetic_moment:  # / muB
        relative_density: #
        </pre>

        <h2>Composits</h2>

        <pre>
        stack: vacuum | C3O3H8 12 | water
        composits:
          water:
            composition:
              H2O: 0.6
              D2O: 0.4
        </pre>
        """)

        text.setHtml(html)
        text.setOpenExternalLinks(True)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.close)

        layout.addWidget(text)
        layout.addWidget(ok_button)

        self.setLayout(layout)
        self.resize(600, 850)


class TabFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            parent = obj.parent()

            if isinstance(obj, (QTextEdit, QPlainTextEdit)) or \
               isinstance(parent, (QTextEdit, QPlainTextEdit)):

                editor = obj if isinstance(obj, (QTextEdit, QPlainTextEdit)) else parent
                editor.insertPlainText("  ")
                return True

        return super().eventFilter(obj, event)

class YamlHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # --- Define formats ---
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#268bd2"))  # blue
        self.key_format.setFontWeight(QFont.Bold)

        self.value_format = QTextCharFormat()
        self.value_format.setForeground(QColor("#2aa198"))  # cyan

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#93a1a1"))  # gray
        self.comment_format.setFontItalic(True)

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#d33682"))  # pink

        self.bool_format = QTextCharFormat()
        self.bool_format.setForeground(QColor("#859900"))  # green
        self.bool_format.setFontWeight(QFont.Bold)

        # --- Regex rules ---
        self.rules = [
            (re.compile(r'#.*'), self.comment_format),
            (re.compile(r'^[ \t]*[\w\-]+(?=\s*:)'), self.key_format),
            (re.compile(r':\s*([^\n#]*)'), self.value_format),
            (re.compile(r'\b-?\d+(\.\d+)?\b'), self.number_format),
            (re.compile(r'\b(true|false|yes|no)\b', re.IGNORECASE), self.bool_format),
            (re.compile(r'^[ \t]*-\s+.+'), self.value_format),
        ]

    def highlightBlock(self, text):
        # this **must exist**, otherwise NotImplementedError
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


class HistoryWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):

        def get_model_and_geometry(modelHistoryDict: dict, sample_name: str, timestamp: float):
            modelHistoryDict[sample_name] = dict()

            # Evaluate the last ten seconds
            starttime = timestamp - 10
            stoptime = timestamp

            # Get last entry
            orsomodel_yaml = None
            for orsomodel_yaml in iter(self.client.ask(
                'gethistory', 'sample/orsomodel_yaml', starttime, stoptime, 1, default=[]
            )):
                pass
            geometry = None
            for geometry in iter(self.client.ask(
                'gethistory', 'sample/geometry', starttime, stoptime, 1, default=[]
            )):
                pass

            # orsomodel_yaml and geometry are either None or a tuple
            # (timestamp, model). We just care for the model, hence we
            # read out the first tuple entry (zeroth is timestamp).
            if orsomodel_yaml is not None:
                modelHistoryDict[sample_name]['orsomodel_yaml'] = orsomodel_yaml[1]

            if geometry is not None:
                modelHistoryDict[sample_name]['geometry'] = geometry[1]

        try:
            from time import time as currenttime

            modelHistoryDict = {}

            # What is the current proposal ID?
            current_prop_id = self.client.eval('session.experiment.proposal', '')

            # Stores the name of the previous sample whose proposal ID matched
            # the current one
            prev_valid_sample_name = None

            # Current time
            now = currenttime()

            # Iterate through sample history. If the proposal ID at the
            # timestamp of a new sample matches the current one, the sample name
            # is stored. Then, when the timestamp of the next sample name is
            # found, we look slightly into the past (last 10 seconds before new
            # sample name was set) and take the latest model and geometry data
            # we can find. This way, we make sure that the history represents
            # the latest state of the model (i.e. before a new one was created).
            for (timestamp, samplename) in self.client.ask(
                'gethistory', 'sample/samplename', 0, now, 1, default=[]
            ):
                if not samplename:
                    continue

                # Get proposal ID at timestamp
                proposal_id = next(iter(self.client.ask(
                    'gethistory', 'Exp/proposal', timestamp, timestamp, 1, default=[]
                )), None)

                if prev_valid_sample_name:
                    get_model_and_geometry(modelHistoryDict, prev_valid_sample_name, timestamp)

                # Does the proposal ID at timestamp match the current proposal id?
                if proposal_id and proposal_id[1] == current_prop_id:
                    prev_valid_sample_name = samplename
                else:
                    prev_valid_sample_name = None

            # For the last sample name, just perform the same procedure, using current tim
            if prev_valid_sample_name:
                get_model_and_geometry(modelHistoryDict, prev_valid_sample_name, now)

            self.finished.emit(modelHistoryDict)

        except Exception as e:
            self.error.emit(str(e))

class SamplePanel(Panel):

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource(
            'nicos_sinq/amor/gui/panels/sample.ui')
        )

        self.filter = TabFilter()
        self.modelEditor = QTextEdit()
        self.modelEditor.setPlainText('stack:')
        self.modelEditor.installEventFilter(self.filter)
        self.modelEditor.textChanged.connect(self.on_text_changed)
        self.modelEditor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # At the start, no thread is running
        self._historyThread = None

        # Keep the highlighter alive
        self.highlighter = YamlHighlighter(self.modelEditor.document())

        # If orsopy is available, add the model
        if orsopy:
            splitter = QSplitter(Qt.Horizontal)
            splitter.addWidget(self.modelEditor)
            splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            viewer = SampleViewer()
            viewer.setObjectName("modelViewer")
            viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            viewer.setMinimumSize(100, 100)
            self.modelViewer = viewer
            splitter.addWidget(viewer)
            self.modelViewer.show_outdated()

            self.modelShowLayout.addWidget(splitter)
        else:
            self.modelShowLayout.addWidget(self.modelEditor)

        self.modelHistory.currentItemChanged.connect(self.on_item_changed)

        # This dict stores sample names as keys and the orsomodel (yaml-string)
        # as item
        self.modelHistoryDict = {}
        self.client.connected.connect(self.on_connected)
        self.reset()

        # Destroy the help window, if it exist
        self.help = None # Placeholder for help window
        self.destroyed.connect(self.on_destroyed)

        # TODO: The history doesn't work properly, hidden until it has been fixed
        # self.modelHistoryLabel.setVisible(False)
        # self.modelHistory.setVisible(False)
        # self.updateHistory.setVisible(False)

        # If the orsomodel has been evaluated successfully by orsopy, this
        # member variable holds a reference to it
        self.orsopyModel = None

    def showEvent(self, event):
        super().showEvent(event)
        self.on_tab_activated()

    def on_tab_activated(self):
        # Read the model from the sample and populate the fields
        self.sampleName.setText(self.client.eval('session.experiment.sample.samplename', ''))

        # Update the geometry entries
        self.update_geometry(self.client.eval('session.experiment.sample.geometry', {}))

        # Update the model
        yamlstr = self.client.eval('session.experiment.sample.orsomodel_yaml', DEFAULT_MODEL)
        self.modelEditor.setText(yamlstr.replace('null', ''))

        # Visualize it, if possible
        self.on_visualizeModel_clicked()

        # Deselect the history entry
        self.modelHistory.selectionModel().clear()

    def update_geometry(self, geometry):
        if not geometry:
            self.xSize.setText('')
            self.ySize.setText('')
            index = self.modelShape.findText(DEFAULT_SHAPE)
            if index >= 0:
                self.modelShape.setCurrentIndex(index)
            return

        shape = geometry.get('shape', DEFAULT_SHAPE)
        index = self.modelShape.findText(shape)
        if index >= 0:
            self.modelShape.setCurrentIndex(index)

        if size_x:= geometry.get('size_x', None):
            self.xSize.setText(size_x)
        else:
            self.xSize.setText('')
        if size_y:= geometry.get('size_y', None):
            self.ySize.setText(size_y)
        else:
            self.ySize.setText('')

    def on_connected(self):
        self.on_updateHistory_clicked()

    @pyqtSlot()
    def on_openModel_clicked(self):
        initialdir = self.client.eval('session.experiment.scriptpath', '')
        fn = QFileDialog.getOpenFileName(self,
                                         'Open model',
                                         initialdir,
                                         'Orso model files (*.yaml *.yml)',
                                         )[0]
        if not fn:
            return

        try:
            with open(fn.encode(sys.getfilesystemencoding()),
                      encoding=LOCALE_ENCODING) as f:
                text = f.read()
        except Exception as err:
            return self.showError('Opening file failed: %s' % err)

        # Put the text into the editor window
        self.modelEditor.setPlainText(text)
        self.modelEditor.setFocus()

    @pyqtSlot()
    def on_saveModel_clicked(self):
        initialdir = self.client.eval('session.experiment.scriptpath', '')
        if not os.path.isdir(initialdir):
            initialdir = os.path.expanduser('~')
        initialdir = os.path.join(initialdir, 'model.yaml')

        defaulttext = '.yaml'
        flt = 'Orsomodel files (*.yaml)'
        fn = QFileDialog.getSaveFileName(self, 'Save Orsomodel', initialdir, flt)[0]
        if not fn:
            return
        if not fn.endswith('.yaml'):
            fn += defaulttext

        try:
            with open(fn, 'w', encoding=LOCALE_ENCODING) as f:
                f.write(self.modelEditor.toPlainText())
        except Exception as err:
            self.showError('Writing file failed: %s' % err)
            return False

    def reset(self):
        self.modelEditor.setText(DEFAULT_MODEL)
        self.update_geometry(None)

    @pyqtSlot()
    def on_clearModel_clicked(self):
        self.modelEditor.setText(DEFAULT_MODEL)

    @pyqtSlot()
    def on_updateHistory_clicked(self):

        # Don't start a thread if another one is already running!
        if self._historyThread:
            return

        # Disable the button to indicate that the history is currently being
        # updated
        self.updateHistory.setEnabled(False)

        # Use a unique attribute name to store the QThread
        self._historyThread = QThread(self)
        self._historyWorker = HistoryWorker(self.client)
        self._historyWorker.moveToThread(self._historyThread)

        # Start work
        self._historyThread.started.connect(self._historyWorker.run)

        # Handle results
        self._historyWorker.finished.connect(self.on_history_ready)
        self._historyWorker.error.connect(self.showError)

        # Cleanup after finished
        self._historyWorker.finished.connect(self._historyThread.quit)
        self._historyWorker.finished.connect(self._historyWorker.deleteLater)
        self._historyThread.finished.connect(self._historyThread.deleteLater)

        # Start the thread
        self._historyThread.start()

    def on_history_ready(self, modelHistoryDict):
        self.modelHistoryDict = modelHistoryDict
        self.modelHistory.clear()
        self.modelHistory.addItems(self.modelHistoryDict.keys())

        # Reenable the button, since the history has been updated
        self.updateHistory.setEnabled(True)

        self._historyThread = None

    def on_item_changed(self, current, _):
        if current:
            self.sampleName.setText(current.text())
            if entry := self.modelHistoryDict.get(current.text(), None):
                if model := entry.get('orsomodel_yaml', None):
                    self.modelEditor.setText(model.replace('null', ''))
                else:
                    self.modelEditor.setText(DEFAULT_MODEL)
                self.update_geometry(entry.get('geometry', None))
            else:
                self.reset()

    @pyqtSlot()
    def on_modelHelp_clicked(self):
        self.help = HelpDialog()
        self.help.destroyed.connect(self.on_help_destroyed)
        self.help.show()

    @pyqtSlot()
    def on_visualizeModel_clicked(self):
        if self.orsopyModel:
            try:
                self.modelViewer.show_sample_model(self.orsopyModel)
            except Exception:
                self.modelViewer.show_cannot_visualize()
        else:
            self.modelViewer.show_cannot_visualize()

    def on_help_destroyed(self):
        self.help = None

    @pyqtSlot()
    def on_applyModel_clicked(self):
        self.client.run('session.experiment.sample.samplename = %r' % self.sampleName.text())
        self.client.run("session.experiment.sample.geometry = {'shape': %r, 'size_x': %r," \
                        "'size_y': %r, 'unit': %r}" % (self.modelShape.currentText(),
                        self.xSize.text(), self.ySize.text(), self.xUnit.text()))
        self.client.run('session.experiment.sample.orsomodel = %r' %
                        dict(yaml.safe_load(self.modelEditor.toPlainText())))
        self.on_updateHistory_clicked()

    def on_text_changed(self):
        if orsopy:
            self.modelViewer.show_outdated()
            try:
                self.orsopyModel = ml.SampleModel.from_dict(yaml.safe_load(self.modelEditor.toPlainText()))
            except Exception:
                self.modelValidationFeedback.setText('invalid model')
                self.modelValidationFeedback.setStyleSheet("color: red;")
                self.orsopyModel = None
                return False
            else:
                self.modelValidationFeedback.setText('valid model')
                self.modelValidationFeedback.setStyleSheet("color: green;")
                return True
        self.modelValidationFeedback.setText('orsopy not installed, cannot validate model')
        self.modelValidationFeedback.setStyleSheet("color: black;")
        return True

    def on_destroyed(self):
        if self.help is not None:
            self.help.destroy()
