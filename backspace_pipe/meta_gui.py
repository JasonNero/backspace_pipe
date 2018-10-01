from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets

from backspace_pipe import core


class MetaGUI(QtWidgets.QWidget):

    def __init__(self):
        # Get Maya Window Pointer (py2: long(ptr), py3: ptr)
        ptr = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(ptr), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace - MetaData")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        self.gui()
        self.show()

    def gui(self):

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
        header_btn = QtWidgets.QPushButton("MetaData GUI")
        # header_btn.clicked.connect(core.scene_controller.meta.load_metafile)
        header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")
        grid_layout.addWidget(header_btn, 0, 0, 1, 3)

        asset_label = QtWidgets.QLabel("Asset:")
        user_label = QtWidgets.QLabel("User:")
        time_label = QtWidgets.QLabel("Time:")
        comment_label = QtWidgets.QLabel("Comment:")
        recent_label = QtWidgets.QLabel("Recent:")
        current_label = QtWidgets.QLabel("Current:")

        asset_qtext = QtWidgets.QLineEdit(core.scene_controller.meta.asset)
        user_qtext = QtWidgets.QLineEdit(core.scene_controller.meta.user)
        time_qtext = QtWidgets.QLineEdit(core.scene_controller.meta.time)
        comment_qtext = QtWidgets.QLineEdit(core.scene_controller.meta.comment)
        recent_qtext = QtWidgets.QLineEdit(core.scene_controller.meta.recent_file)
        current_qtext = QtWidgets.QLineEdit(core.scene_controller.meta.current_file)

        asset_qtext.setReadOnly(True)
        user_qtext.setReadOnly(True)
        time_qtext.setReadOnly(True)
        comment_qtext.setReadOnly(True)
        recent_qtext.setReadOnly(True)
        current_qtext.setReadOnly(True)

        grid_layout.addWidget(asset_label, 1, 0)
        grid_layout.addWidget(asset_qtext, 1, 1, 1, 2)

        grid_layout.addWidget(user_label, 2, 0)
        grid_layout.addWidget(user_qtext, 2, 1, 1, 2)

        grid_layout.addWidget(time_label, 3, 0)
        grid_layout.addWidget(time_qtext, 3, 1, 1, 2)

        grid_layout.addWidget(comment_label, 4, 0)
        grid_layout.addWidget(comment_qtext, 4, 1, 1, 2)

        grid_layout.addWidget(recent_label, 5, 0)
        grid_layout.addWidget(recent_qtext, 5, 1, 1, 2)

        grid_layout.addWidget(current_label, 6, 0)
        grid_layout.addWidget(current_qtext, 6, 1, 1, 2)

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(core.scene_controller.meta.load_metafile)

        grid_layout.addWidget(refresh_btn, 7, 1, 1, 2)

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

        # Add Layouts to Window
        top_level_layout.addLayout(grid_layout)

        # Add Layout to window
        self.setLayout(top_level_layout)
