from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets

import backspace_pipe.exporter as exporter


''' TODO: 
- Add Custom Comment
- Advanced Tab -> Overwrite Existing, Optional Comment
'''


class ExporterGUI(QtWidgets.QWidget):

    def __init__(self):
        pointer = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(pointer), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace - Exporter")
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)

        self.gui()
        self.show()

    def gui(self):

        # Create Top Level Layout
        top_level_layout = QtWidgets.QHBoxLayout(self)

        # Header Button
        header_btn = QtWidgets.QPushButton("Exporter GUI")
        # header_btn.clicked.connect(scene_controller.get_instance().meta.load_metafile)
        header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")

        # OBJ
        obj_box = QtWidgets.QGroupBox(self, title="OBJ Export")
        obj_box_layout = QtWidgets.QVBoxLayout(self)
        obj_box_layout.setMargin(5)
        self.obj_info_label = QtWidgets.QLabel("Packages: Painter/Designer")
        self.obj_info_label.setMinimumWidth(150)
        self.obj_smooth_check = QtWidgets.QCheckBox(checked=True, text="Smooth")
        self.obj_tri_check = QtWidgets.QCheckBox(checked=True, text="Triangulate")
        obj_exec_btn = QtWidgets.QPushButton("Export")
        obj_exec_btn.setEnabled(False)

        obj_exec_btn.clicked.connect(self.execute_obj)

        obj_box_layout.addWidget(self.obj_info_label)
        obj_box_layout.addWidget(self.obj_smooth_check)
        obj_box_layout.addWidget(self.obj_tri_check)
        obj_box_layout.addWidget(obj_exec_btn)
        obj_box.setLayout(obj_box_layout)

        # FBX
        fbx_box = QtWidgets.QGroupBox(self, title="FBX Export")
        fbx_box_layout = QtWidgets.QVBoxLayout(self)
        fbx_box_layout.setMargin(5)
        self.fbx_info_label = QtWidgets.QLabel("Packages: Mari")
        self.fbx_info_label.setMinimumWidth(150)
        self.fbx_smooth_check = QtWidgets.QCheckBox(checked=False, text="Smooth")
        self.fbx_tri_check = QtWidgets.QCheckBox(checked=False, text="Triangulate")
        fbx_exec_btn = QtWidgets.QPushButton("Export")

        fbx_exec_btn.clicked.connect(self.execute_fbx)

        fbx_box_layout.addWidget(self.fbx_info_label)
        fbx_box_layout.addWidget(self.fbx_smooth_check)
        fbx_box_layout.addWidget(self.fbx_tri_check)
        fbx_box_layout.addWidget(fbx_exec_btn)
        fbx_box.setLayout(fbx_box_layout)

        # Add Layouts to Window
        top_level_layout.addWidget(obj_box)
        top_level_layout.addWidget(fbx_box)

        # Add Layout to window
        self.setLayout(top_level_layout)

    def execute_obj(self):
    	exporter.export_selected_obj(force=True, triangulate=self.obj_tri_check.isChecked(), smooth=self.obj_smooth_check.isChecked())

    def execute_fbx(self):
    	exporter.export_selected_fbx(force=True, triangulate=self.fbx_tri_check.isChecked(), smooth=self.fbx_smooth_check.isChecked())
