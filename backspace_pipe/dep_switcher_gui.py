from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets

import backspace_pipe.dep_switcher as dep_switcher


''' TODO: 
- Add Custom Comment
- Advanced Tab -> Overwrite Existing, Optional Comment
'''


class SwitcherGUI(QtWidgets.QWidget):

    def __init__(self):
        pointer = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(pointer), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace - Dep Switcher")
        self.setMinimumWidth(100)
        self.setMinimumHeight(100)

        self.gui()
        self.show()

    def gui(self):

        # Create Top Level Layout
        top_level_layout = QtWidgets.QVBoxLayout(self)

        # Header Button
        self.header_btn = QtWidgets.QPushButton("Dep Switcher")
        self.header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")

        # OBJ
        self.old_dep_text = QtWidgets.QLineEdit("MDL")
        self.new_dep_text = QtWidgets.QLineEdit("SHD")
        self.replace_check = QtWidgets.QCheckBox(checked=True, text="Replace")
        self.exec_btn = QtWidgets.QPushButton("Execute")

        self.exec_btn.clicked.connect(self.execute)

        top_level_layout.addWidget(self.header_btn)
        top_level_layout.addWidget(self.old_dep_text)
        top_level_layout.addWidget(self.new_dep_text)
        top_level_layout.addWidget(self.replace_check)
        top_level_layout.addWidget(self.exec_btn)

        # Add Layout to window
        self.setLayout(top_level_layout)

    def execute(self):
        dep_switcher.switch(curr_dep=self.old_dep_text.text(), new_dep=self.new_dep_text.text(), replace=self.replace_check.isChecked())
