from maya import OpenMayaUI as omui
from PySide2 import QtCore, QtWidgets, QtGui
from functools import partial
import getpass

from shiboken2 import wrapInstance

from backspace_pipe import toolbox_func, logging_control, constants

start_text = '''########################################################
Backspace Pipe - Logging
Current Toolbox: {toolbox}
Current User:    {user}
########################################################
'''


class ScrollAreaWidget(QtWidgets.QScrollArea):
    fileDropped = QtCore.Signal(list)

    def __init__(self, enable_drop_files=False, only_local_files=False, *args, **kwargs):
        super(ScrollAreaWidget, self).__init__(*args, **kwargs)
        self._enable_drop_files = enable_drop_files
        self._only_local_files = only_local_files

        self.setupWidget()

    def setupWidget(self):
        self.setAutoFillBackground(True)
        if not self._enable_drop_files:
            self.scrollarea_widget = QtWidgets.QWidget()
        # else:
        #     self.scrollarea_widget = DropFileWidget(only_local_files=self._only_local_files)
        #     self.scrollarea_widget.fileDropped.connect(self.emit_drop_file)

        self.scrollarea_widget.setAutoFillBackground(True)
        self.setWidgetResizable(True)
        self.setWidget(self.scrollarea_widget)
        self.scrollarea_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def emit_drop_file(self, links):
        self.fileDropped.emit(links)

    def setLayout(self, *args, **kwargs):
        self.scrollarea_widget.setLayout(*args, **kwargs)

    def layout(self, *args, **kwargs):
        self.scrollarea_widget.layout(self, *args, **kwargs)

    def update(self, *args, **kwargs):
        try:
            self.updateLayout()
        except Exception:
            pass
        QtWidgets.QScrollArea.update(self, *args, **kwargs)

    def repaint(self, *args, **kwargs):
        try:
            self.updateLayout()
        except Exception:
            pass
        self.scrollarea_widget.repaint()
        QtWidgets.QScrollArea.repaint(self, *args, **kwargs)

    def updateLayout(self):
        if self.layout():
            self.scrollarea_widget.setMinimumSize(self.layout().totalSizeHint())
            # logger.debug(self.layout().totalSizeHint().height())
            self.scrollarea_widget.repaint()


# class DropFileWidget(QtWidgets.QWidget):
#     fileDropped = QtCore.Signal(list)

#     def __init__(self, only_local_files=False, *args, **kwargs):
#         super(DropFileWidget, self).__init__(*args, **kwargs)
#         self._onlyLocalFiles = only_local_files
#         self.setAcceptDrops(True)
#         self._lastDroppedFiles = []

#     def lastDroppedFileList(self):
#         return self._lastDroppedFiles

#     def dragEnterEvent(self, event, *args, **kwargs):
#         if event.mimeData().hasUrls:
#             event.accept()
#         else:
#             event.ignore()

#     def dragMoveEvent(self, event, *args, **kwargs):
#         if event.mimeData().hasUrls():
#             event.setDropAction(QtCore.Qt.CopyAction)
#             event.accept()
#         else:
#             event.ignore()

#     def dropEvent(self, event, *args, **kwargs):
#         if event.mimeData().hasUrls():
#             event.setDropAction(QtCore.Qt.CopyAction)
#             event.accept()
#             links = []
#             for url in event.mimeData().urls():
#                 if url.toLocalFile():
#                     links.append(str(url.toLocalFile()))
#                 elif not self._onlyLocalFiles:
#                     temp_file = urllib.urlretrieve(str(url.toString()))
#                     temp_rename_file = os.path.normpath(os.path.join(str(os.path.split(temp_file[0])[0]), str(os.path.split(url.toString())[1])))
#                     try:
#                         os.rename(temp_file[0], temp_rename_file)
#                     except Exception:
#                         links.append(str(temp_file[0]))
#                     else:
#                         links.append(str(temp_rename_file))
#                 else:
#                     pass
#             self._lastDroppedFiles = links
#             self.fileDropped.emit(links)
#         else:
#             event.ignore()


class GUI(QtWidgets.QWidget):

    # [initial_checkbox_checked, label_text, button_function, checkbox_obj, button_obj]
    # Maybe use a dict or classes even custom widgets instead?

    toolbox_array_mod_setup = [
        [True, "Save on setup", toolbox_func.save_on_setup, None, None],
        [True, "Create deleteOnPublish set", toolbox_func.create_delOnPub_set, None, None],
        [True, "Create refsToImport set", toolbox_func.create_refsToImport_set, None, None],
        [True, "Delete unknown DAG Nodes", toolbox_func.del_unknown_dag, None, None],
        [True, "Delete display layers", toolbox_func.del_displaylayers, None, None],
        [True, "Delete ALL history", toolbox_func.del_all_history, None, None],
        [True, "Assure unique naming", toolbox_func.assure_unique_naming, None, None],
        [True, "Assure matching shape <-> transf names", toolbox_func.assure_shape_names, None, None],
        [True, "Mesh cleanup check", toolbox_func.mesh_check, None, None]
    ]

    toolbox_array_mod_publish = [
        [True, "Fit view to all elements", toolbox_func.fit_view, None, None],
        [True, "Delete unknown DAG Nodes", toolbox_func.del_unknown_dag, None, None],
        [True, "Assure unique naming", toolbox_func.assure_unique_naming, None, None],
        [True, "Assure matching shape <-> transf names", toolbox_func.assure_shape_names, None, None],
        [True, "Mesh cleanup check", toolbox_func.mesh_check, None, None],
        [True, "Check for non-uniform shape scaling", toolbox_func.check_nonuniform_scale, None, None],
        [True, "Incremental Save", toolbox_func.incremental_save, None, None],
        [True, "Import refsToImport set", toolbox_func.import_refs_set, None, None],
        [False, "Remove all References", toolbox_func.rem_all_refs, None, None],
        [True, "Delete deleteOnPublish set", toolbox_func.del_delOnPub_set, None, None],
        [True, "Delete display layers", toolbox_func.del_displaylayers, None, None],
        [True, "Delete ALL history", toolbox_func.del_all_history, None, None],
        [True, "Assure lambert1 on all geo", toolbox_func.assure_lambert1, None, None],
        [True, "Delete Non-Default Cameras", toolbox_func.delete_nondefault_cameras, None, None],
        [True, "Delete unused Nodes", toolbox_func.delete_unused_nodes, None, None],
        [True, "Delete Pipeline Sets", toolbox_func.delete_sets, None, None],
        [True, "Reset Viewport Subdiv", toolbox_func.unsmooth_all, None, None],
        [True, "PUBLISH [MA]", toolbox_func.publish, None, None],
        [True, "Send Slack Publish Notification", toolbox_func.slack_publish_notification, None, None],
        [True, "Close Scene", toolbox_func.close_scene, None, None],
        [True, "Open last incremental save", toolbox_func.open_last_increment, None, None]
    ]

    toolbox_array_shd_setup = [
        [True, "Create deleteOnPublish set", toolbox_func.create_delOnPub_set, None, None],
        [True, "Delete unknown DAG Nodes", toolbox_func.del_unknown_dag, None, None],
        [True, "Make sure model is referenced", toolbox_func.is_mdl_referenced, None, None],
        [True, "Set default aiSubdiv for all Shapes", toolbox_func.set_default_aiSubdiv, None, None],
        [True, "Set default aiVisibility for all Shapes", toolbox_func.set_default_aiVisibility, None, None],
        [True, "Reference Shading Lightset", toolbox_func.ref_shading_lightset, None, None]
    ]

    toolbox_array_shd_publish = [
        [True, "Fit view to all elements", toolbox_func.fit_view, None, None],
        [True, "Delete unknown DAG Nodes", toolbox_func.del_unknown_dag, None, None],
        [True, "Close Arnold Renderview to prevent crash", toolbox_func.close_ai_view, None, None],
        [True, "Check input file paths", toolbox_func.check_input_paths, None, None],
        [True, "Incremental Save", toolbox_func.incremental_save, None, None],
        [True, "Remove unloaded References", toolbox_func.rem_unloaded_refs, None, None],
        [True, "Remove Shading Lightset", toolbox_func.deref_shading_lightset, None, None],
        [True, "Remove Ref Edits (translate, rotate, scale)", toolbox_func.rem_ref_edits, None, None],
        [True, "Delete deleteOnPublish set", toolbox_func.del_delOnPub_set, None, None],
        [True, "Update *.tx files", toolbox_func.create_tx, None, None],
        [True, "Delete display layers", toolbox_func.del_displaylayers, None, None],
        [True, "Delete ALL history", toolbox_func.del_all_history, None, None],
        [True, "Delete Non-Default Cameras", toolbox_func.delete_nondefault_cameras, None, None],
        [True, "PUBLISH [ASS]", toolbox_func.publish_ass, None, None],
        [True, "PUBLISH [MA]", toolbox_func.publish, None, None],
        [True, "Send Slack Publish Notification", toolbox_func.slack_publish_notification, None, None],
        [True, "Close Scene", toolbox_func.close_scene, None, None],
        [True, "Open last incremental save", toolbox_func.open_last_increment, None, None]
    ]

    def __init__(self, toolbox="mod_setup"):
        self.toolbox_str = toolbox.lower()

        pointer = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(pointer), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace Toolbox")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        self._qsettings = QtCore.QSettings("CA", "Backspace")

        # Set current Toolbox
        if self.toolbox_str == "mod_setup":
            self.toolbox_array = self.toolbox_array_mod_setup
        elif self.toolbox_str == "mod_publish":
            self.toolbox_array = self.toolbox_array_mod_publish
        elif self.toolbox_str == "shd_setup":
            self.toolbox_array = self.toolbox_array_shd_setup
        elif self.toolbox_str == "shd_publish":
            self.toolbox_array = self.toolbox_array_shd_publish
        else:
            self.toolbox_array = ""

        self.gui()
        self._load_settings()
        self.show()

    def _load_settings(self):
        state = self._qsettings.value('%s/mainsplitter' % self.toolbox_str)
        if state:
            self.v_splitter.restoreState(state)

    def _save_settings(self):
        self._qsettings.setValue('%s/mainsplitter' % self.toolbox_str, self.v_splitter.saveState())

    def closeEvent(self, event):
        self._save_settings()
        return QtWidgets.QWidget.closeEvent(self, event)

    def gui(self):
        self.connect(self, QtCore.SIGNAL("sendValue(PyObject)"), self.handleReturn)

        # Create Top Level Layout
        top_level_layout = QtWidgets.QVBoxLayout(self)
        top_level_layout.setContentsMargins(0, 0, 0, 0)

        checklist_wdg = QtWidgets.QWidget()

        # Create Grid Layout
        grid_layout = QtWidgets.QGridLayout(checklist_wdg)

        # Header Button
        header_btn = QtWidgets.QPushButton("{} TOOLBOX".format(self.toolbox_str.upper()))
        header_btn.setStyleSheet("background-color: rgb(50, 115, 35)")
        grid_layout.addWidget(header_btn, 0, 0, 1, 2)

        # Create Checkbox Button Rows from array
        for row in self.toolbox_array:
            # Get Rowcount
            next_row = grid_layout.rowCount() + 1

            # Create Checkbox from array
            checkbox = QtWidgets.QCheckBox(checked=row[0], text=row[1])

            # Create Button from array and connect it
            button = QtWidgets.QPushButton("execute")
            self.connect(button, QtCore.SIGNAL("clicked()"), partial(self.attach_signal_emitter, row[2]))

            # Save Objects in the array
            row[3] = checkbox
            row[4] = button

            # Add widgets to layout
            grid_layout.addWidget(checkbox, next_row, 0)
            grid_layout.addWidget(button, next_row, 1)

        # Execute All Button
        execute_all_btn = QtWidgets.QPushButton("Execute all")
        self.connect(execute_all_btn, QtCore.SIGNAL("clicked()"), self.execute_all)

        # Fix Cursor Button
        fix_cursor_btn = QtWidgets.QPushButton("CursorFix")
        self.connect(fix_cursor_btn, QtCore.SIGNAL("clicked()"), toolbox_func.toggle_wait_cursor)

        # Add Execute and Cursor Button to layout
        next_row = grid_layout.rowCount() + 1
        grid_layout.addWidget(fix_cursor_btn, next_row, 1)
        grid_layout.addWidget(execute_all_btn, next_row, 0, 1, 1)

        # Some Layouting (Spacing between elements, row/column resize when window resized)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setRowStretch(0, 10)
        grid_layout.setSpacing(4)

        # ===== LOGGING GUI START =====

        # Create loggerbox with title Logging
        loggerbox = QtWidgets.QGroupBox(self, title="Logging")
        loggerbox_layout = QtWidgets.QVBoxLayout(self)
        loggerbox_layout.setMargin(5)

        # Create and layout Text Widget
        textedit = QtWidgets.QPlainTextEdit(self, readOnly=True)
        # textedit.setMaximumHeight(100)

        # Create and Apply monospaced font
        textedit_font = QtGui.QFont("Consolas")
        textedit.setFont(textedit_font)

        # Start Text for Log Widget
        start_text_formatted = start_text.format(toolbox=self.toolbox_str, user=getpass.getuser()).replace(" ", "&nbsp;").replace("\n", "<br>")
        start_html = "<p><font color='LightSeaGreen'>{}</font></p>".format(start_text_formatted)
        textedit.appendHtml(start_html)

        # Add Widget as Logging Output
        logging_control.add_handler(constants.LogMode.QTEXT, textedit)

        loggerbox_layout.addWidget(textedit)
        loggerbox.setLayout(loggerbox_layout)

        # ===== LOGGING GUI END =====
        self.v_splitter = QtWidgets.QSplitter(orientation=QtCore.Qt.Vertical)
        top_level_layout.addWidget(self.v_splitter)

        scrollarea = ScrollAreaWidget(enable_drop_files=False)
        scrollarea_vlay = QtWidgets.QVBoxLayout()
        scrollarea.setLayout(scrollarea_vlay)
        scrollarea_vlay.addWidget(checklist_wdg)

        self.v_splitter.addWidget(scrollarea)
        self.v_splitter.addWidget(loggerbox)

        # Add Layouts to Window
        # top_level_layout.addLayout(grid_layout)
        # top_level_layout.addWidget(loggerbox)

        # Add Layout to window
        # self.setLayout(top_level_layout)

    def execute_all(self):
        for i, row in enumerate(self.toolbox_array):
            # check Checkbox for current row
            if row[3].isChecked():
                rowSuccessful = self.attach_signal_emitter(row[2])
            else:
                continue

            if rowSuccessful:
                continue
            else:
                break

    # Emit Signal Function
    def attach_signal_emitter(self, orig_func):
        result = orig_func()
        emission = [orig_func, result]
        self.emit(QtCore.SIGNAL("sendValue(PyObject)"), emission)
        return result

    # Receive Signal Function
    def handleReturn(self, emission):
        btn = self.get_btn_from_func(emission[0])
        if emission[1]:
            btn.setStyleSheet("background-color: rgb(60, 200, 80)")
        else:
            btn.setStyleSheet("background-color: rgb(200, 40, 10)")

    def get_btn_from_func(self, func):
        for row in self.toolbox_array:
            if row[2] == func:
                return row[4]
