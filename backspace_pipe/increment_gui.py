from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets, QtGui
from functools import partial
import getpass

from backspace_pipe import logging_control, constants

start_text = '''########################################################
Backspace Pipe - Logging
Current Toolbox: {toolbox}
Current User:    {user}
########################################################
'''


class IncrementGUI(QtWidgets.QWidget):

    def __init__(self):
        # Get Maya Window Pointer (py2: long(ptr), py3: ptr)
        ptr = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(ptr), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace - IncrementGUI")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        self.gui()
        self.show()

    def gui(self):
        self.connect(self, QtCore.SIGNAL("sendValue(PyObject)"), self.handleReturn)

        # Create Top Level Layout
        top_level_layout = QtWidgets.QVBoxLayout(self)

        # # Create Menu Bar
        # self.main_menu = QtWidgets.QMenuBar()
        # test_menu = self.main_menu.addMenu("Test")
        # asdf_menu = self.main_menu.addMenu("asdf")

        # top_level_layout.addWidget(self.main_menu)

        # Create Grid Layout
        grid_layout = QtWidgets.QGridLayout(self)

        # Header Button
        header_btn = QtWidgets.QPushButton("IncrementGUI")
        header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")
        grid_layout.addWidget(header_btn, 0, 0, 1, 3)

        curr_scene_label = QtWidgets.QLabel("Current:")
        incr_scene_label = QtWidgets.QLabel("Increment:")
        comment_label = QtWidgets.QLabel("Comment:")

        curr_scene_qtext = QtWidgets.QLineEdit("current_scene_01.maaaa")
        curr_scene_qtext.setReadOnly(True)
        incr_scene_qtext = QtWidgets.QLineEdit("current_scene_02.maaaa")
        incr_scene_qtext.setReadOnly(True)
        comment_qtext = QtWidgets.QTextEdit("some comments")
        comment_qtext.setFixedHeight(60)

        save_btn = QtWidgets.QPushButton("Save!")
        save_btn.setMinimumWidth(100)
        save_btn.setMinimumHeight(30)

        grid_layout.addWidget(curr_scene_label, 1, 0)
        grid_layout.addWidget(curr_scene_qtext, 1, 1, 1, 2)
        grid_layout.addWidget(incr_scene_label, 2, 0)
        grid_layout.addWidget(incr_scene_qtext, 2, 1, 1, 2)
        grid_layout.addWidget(comment_label, 3, 0)
        grid_layout.addWidget(comment_qtext, 3, 1, 1, 2)
        grid_layout.addWidget(save_btn, 5, 1)

        # # Execute All Button
        # execute_all_btn = QtWidgets.QPushButton("Execute all")
        # self.connect(execute_all_btn, QtCore.SIGNAL("clicked()"), self.execute_all)

        # # Fix Cursor Button
        # fix_cursor_btn = QtWidgets.QPushButton("CursorFix")
        # self.connect(fix_cursor_btn, QtCore.SIGNAL("clicked()"), toolbox_func.toggle_wait_cursor)

        # Some Layouting (Spacing between elements, row/column resize when window resized)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(0, 10)
        grid_layout.setSpacing(4)

        # ===== LOGGING GUI START =====

        # Create loggerbox with title Logging
        loggerbox = QtWidgets.QGroupBox(self, title="Logging")
        loggerbox_layout = QtWidgets.QVBoxLayout(self)
        loggerbox_layout.setMargin(5)

        # Create and layout Text Widget
        textedit = QtWidgets.QPlainTextEdit(self, readOnly=True)
        textedit.setMaximumHeight(100)

        # Create and Apply monospaced font
        textedit_font = QtGui.QFont("Consolas")
        textedit.setFont(textedit_font)

        # Start Text for Log Widget
        start_text_formatted = start_text.format(toolbox="IncrementGUI", user=getpass.getuser()).replace(" ", "&nbsp;").replace("\n", "<br>")
        start_html = "<p><font color='LightSeaGreen'>{}</font></p>".format(start_text_formatted)
        textedit.appendHtml(start_html)

        # Add Widget as Logging Output
        logging_control.add_handler(constants.LogMode.QTEXT, textedit)

        loggerbox_layout.addWidget(textedit)
        loggerbox.setLayout(loggerbox_layout)

        # ===== LOGGING GUI END =====

        # Add Layouts to Window
        top_level_layout.addLayout(grid_layout)
        top_level_layout.addWidget(loggerbox)

        # Add Layout to window
        self.setLayout(top_level_layout)

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
