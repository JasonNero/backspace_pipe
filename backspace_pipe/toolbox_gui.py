from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets
from functools import partial

from backspace_pipe import toolbox_func


class GUI(QtWidgets.QWidget):

    # [checkbox_enabled, label_text, button_function, checkbox_obj, button_obj]
    # Maybe use a dict instead?

    # toolbox_dict_test = {'checked': True, 'text': 'this is an example', 'func': toolbox_func.toggle_wait_cursor, 'checkbox': None, 'button': None}

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
        [True, "Incremental Save", toolbox_func.incremental_save, None, None],
        [True, "Delete Student License String", toolbox_func.del_maya_lic_string, None, None],
        [True, "Import refsToImport set", toolbox_func.import_refs_set, None, None],
        [True, "Remove all References", toolbox_func.rem_all_refs, None, None],
        [True, "Delete deleteOnPublish set", toolbox_func.del_delOnPub_set, None, None],
        [True, "Delete display layers", toolbox_func.del_displaylayers, None, None],
        [True, "Delete ALL history", toolbox_func.del_all_history, None, None],
        [True, "Assure lambert1 on all geo", toolbox_func.assure_lambert1, None, None],
        [True, "Delete unused Nodes", toolbox_func.delete_unused_nodes, None, None],
        [True, "PUBLISH", toolbox_func.publish, None, None],
        [True, "Delete Student License String", toolbox_func.del_maya_lic_string, None, None],
        [True, "Send Slack Publish Notification", toolbox_func.slack_publish_notification, None, None],
        [True, "Close Scene", toolbox_func.close_scene, None, None],
        [True, "Open last incremental save", toolbox_func.open_last_increment, None, None]
    ]

    def __init__(self, toolbox="mod_setup"):
        self.toolbox = toolbox

        # Get Maya Window Pointer (py2: long(ptr), py3: ptr)
        ptr = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(ptr), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace Toolbox")
        self.setMinimumWidth(400)

        # Set current Toolbox
        if self.toolbox == "mod_setup":
            self.toolbox_array = self.toolbox_array_mod_setup
        elif self.toolbox == "mod_publish":
            self.toolbox_array = self.toolbox_array_mod_publish

        self.gui()
        self.show()

    def gui(self):
        self.connect(self, QtCore.SIGNAL("sendValue(PyObject)"), self.handleReturn)

        # Set Layout
        grid_layout = QtWidgets.QGridLayout(self)

        # Header Button
        header_btn = QtWidgets.QPushButton("{} TOOLBOX".format(self.toolbox.upper()))
        header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")
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

        # Apply Layout to our window
        self.setLayout(grid_layout)

    def execute_all(self):
        for i, row in enumerate(self.toolbox_array):
            # print("Row {} checked: {}".format(i, row[3].isChecked()))
            if not row[3].isChecked():
                continue
            else:
                rowSuccessful = self.attach_signal_emitter(row[2])

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
