from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets

import backspace_pipe.dep_switcher as dep_switcher


class SwitcherGUI(QtWidgets.QWidget):

    def __init__(self):
        pointer = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(pointer), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace - Dep Switcher")
        self.setMinimumWidth(160)
        self.setMinimumHeight(100)

        self.gui()
        self.show()

    def gui(self):

        # Create Top Level Layout
        self.top_level_layout = QtWidgets.QVBoxLayout(self)

        # Header Button
        self.header_btn = QtWidgets.QPushButton("Dep Switcher")
        self.header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")

        # Main Gui
        self.old_dep_layout = QtWidgets.QGridLayout()
        self.old_dep_label = QtWidgets.QLabel("Old Department:")
        self.old_dep_text = QtWidgets.QLineEdit("MDL")
        self.old_dep_text.setFixedWidth(50)

        self.new_dep_layout = QtWidgets.QGridLayout()
        self.new_dep_label = QtWidgets.QLabel("New Department:")
        self.new_dep_text = QtWidgets.QLineEdit("ASS")
        self.new_dep_text.setFixedWidth(50)

        self.replace_check = QtWidgets.QCheckBox(checked=False, text="Replace")
        self.grouped_check = QtWidgets.QCheckBox(checked=True, text="Grouped")
        self.exec_btn = QtWidgets.QPushButton("Execute")

        # Function Connect
        self.exec_btn.clicked.connect(self.execute)

        # Layouting
        self.top_level_layout.addWidget(self.header_btn)

        self.old_dep_layout.addWidget(self.old_dep_label, 0, 0)
        self.old_dep_layout.addWidget(self.old_dep_text, 0, 1)
        self.top_level_layout.addLayout(self.old_dep_layout)

        self.new_dep_layout.addWidget(self.new_dep_label, 0, 0)
        self.new_dep_layout.addWidget(self.new_dep_text, 0, 1)
        self.top_level_layout.addLayout(self.new_dep_layout)

        self.top_level_layout.addWidget(self.replace_check)
        self.top_level_layout.addWidget(self.grouped_check)
        self.top_level_layout.addWidget(self.exec_btn)

        # Add Layout to window
        self.setLayout(self.top_level_layout)

    def execute(self):
        dep_switcher.switch(curr_dep=self.old_dep_text.text(), new_dep=self.new_dep_text.text(), replace=self.replace_check.isChecked(), grouped=self.grouped_check.isChecked())
