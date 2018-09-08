from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets
from functools import partial

import backspace_pipe.toolbox_func as toolbox_func


class GUI(QtWidgets.QWidget):

    # [checkbox_enabled, label_text, button_function, checkbox_obj, button_obj]
    # Maybe use a dict instead?
    toolbox_array_setup = [
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

    toolbox_array_publish = [
        [True, "Fit view to all elements", toolbox_func.fit_view, None, None],
        [True, "Delete unknown DAG Nodes", toolbox_func.del_unknown_dag, None, None],
        [True, "Assure unique naming", toolbox_func.assure_unique_naming, None, None],
        [True, "Assure matching shape <-> transf names", toolbox_func.assure_shape_names, None, None],
        [True, "Mesh cleanup check", toolbox_func.mesh_check, None, None],
        [True, "Incremental Save", toolbox_func.incremental_save, None, None],
        [True, "Import refsToImport set", toolbox_func.import_refs_set, None, None],
        [True, "Remove all References", toolbox_func.rem_all_refs, None, None],
        [True, "Delete deleteOnPublish set", toolbox_func.del_delOnPub_set, None, None],
        [True, "Delete display layers", toolbox_func.del_displaylayers, None, None],
        [True, "Delete ALL history", toolbox_func.del_all_history, None, None],
        [True, "PUBLISH", toolbox_func.publish, None, None],
        [True, "Send Slack Publish Notification", toolbox_func.slack_publish_notification, None, None],
        [True, "Close Scene", toolbox_func.close_scene, None, None]
    ]

    def __init__(self, toolbox="setup"):
        self.toolbox = toolbox

        # Get Maya Window Pointer
        ptr = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(ptr), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace Toolbox")
        self.setMinimumWidth(400)


        if self.toolbox == "setup":
            self.toolbox_array = self.toolbox_array_setup
        elif self.toolbox == "publish":
            self.toolbox_array = self.toolbox_array_publish

        self.gui()
        self.show()

    def gui(self):
        self.connect(self, QtCore.SIGNAL("sendValue(PyObject)"), self.handleReturn)

        grid_layout = QtWidgets.QGridLayout(self)

        header_btn = QtWidgets.QPushButton("{} TOOLBOX".format(self.toolbox.upper()))
        header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")
        grid_layout.addWidget(header_btn, 0, 0, 1, 2)

        for row in self.toolbox_array:
            next_row = grid_layout.rowCount() + 1

            checkbox = QtWidgets.QCheckBox(checked=row[0], text=row[1])
            button = QtWidgets.QPushButton("execute")
            self.connect(button, QtCore.SIGNAL("clicked()"), partial(self.attach_signal_emitter, row[2]))

            row[3] = checkbox
            row[4] = button

            grid_layout.addWidget(checkbox, next_row, 0)
            grid_layout.addWidget(button, next_row, 1)

        execute_all_btn = QtWidgets.QPushButton("Execute all")
        self.connect(execute_all_btn, QtCore.SIGNAL("clicked()"), self.execute_all)

        fix_cursor_btn = QtWidgets.QPushButton("CursorFix")
        self.connect(fix_cursor_btn, QtCore.SIGNAL("clicked()"), toolbox_func.toggle_wait_cursor)

        next_row = grid_layout.rowCount() + 1
        grid_layout.addWidget(fix_cursor_btn, next_row, 1)
        grid_layout.addWidget(execute_all_btn, next_row, 0, 1, 1)
        # grid_layout.addWidget(QtWidgets.QLabel("bla"))

        grid_layout.setColumnStretch(0, 1)
        grid_layout.setRowStretch(0, 10)
        grid_layout.setSpacing(4)

        # execute_btn_01.clicked.connect(self.hello_world)

        self.setLayout(grid_layout)


    def execute_all(self):
        for row in self.toolbox_array:
            if not row[0]:
                continue
            else:
                self.attach_signal_emitter(row[2])


    def attach_signal_emitter(self, orig_func):
        result = orig_func()
        emission = [orig_func, result]
        self.emit(QtCore.SIGNAL("sendValue(PyObject)"), emission)


    def handleReturn(self, value):
        btn = self.get_btn_from_func(value[0])
        if value[1]:
            btn.setStyleSheet("background-color: rgb(60, 200, 80)")
        else:
            btn.setStyleSheet("background-color: rgb(200, 40, 10)")


    def get_btn_from_func(self, func):
        for row in self.toolbox_array:
            if row[2] == func:
                return row[4]
