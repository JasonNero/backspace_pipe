from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets

from backspace_pipe import asset_parser

import pymel.core as pmc


class DresserGUI(QtWidgets.QWidget):

    def __init__(self):
        pointer = omui.MQtUtil.mainWindow()
        parent = wrapInstance(long(pointer), QtWidgets.QWidget)
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Some Variables
        self.asset_list = []
        self.department_filter = "MDL"
        self.sel_items = []

        # Set Maya as parent for our widget (which is flagged as window)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Backspace - Dresser")
        self.setMinimumWidth(300)
        self.setMinimumHeight(500)

        self.asset_list = asset_parser.parse()

        self.gui()
        self.show()

    def gui(self):
        # LAYOUTS
        top_level_layout = QtWidgets.QVBoxLayout(self)
        radio_buttons_layout = QtWidgets.QHBoxLayout(self)
        btn_grid_layout = QtWidgets.QGridLayout(self)

        # Header Button
        header_btn = QtWidgets.QPushButton("Dresser GUI")
        header_btn.setStyleSheet("background-color: rgb(60, 200, 80)")

        # Radio Boxes
        self.mdl_rbox = QtWidgets.QRadioButton("MDL")
        self.shd_rbox = QtWidgets.QRadioButton("SHD")
        self.rig_rbox = QtWidgets.QRadioButton("RIG")
        self.mdl_rbox.setChecked(True)

        rbox_group = [self.mdl_rbox, self.shd_rbox, self.rig_rbox]
        for rbox in rbox_group:
            radio_buttons_layout.addWidget(rbox)
            rbox.toggled.connect(self.dep_rbox_changed)

        # QListWidget
        self.assets_qlist = QtWidgets.QListWidget(self)
        self.assets_qlist.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.assets_qlist.itemSelectionChanged.connect(self.item_sel_changed)

        # QListItems
        self.update_qlist()

        # Reference Button
        reference_btn = QtWidgets.QPushButton("Create References")
        reference_btn.clicked.connect(self.create_references)

        # Amount Box
        self.amount_lineEdit = QtWidgets.QLineEdit("1")
        self.amount_lineEdit.setMaximumWidth(75)

        # # Update Button
        # update_btn = QtWidgets.QPushButton("Update")
        # update_btn.clicked.connect(self.update_qlist)

        # LAYOUTS
        top_level_layout.addWidget(header_btn)
        top_level_layout.addLayout(radio_buttons_layout)
        top_level_layout.addWidget(self.assets_qlist)
        btn_grid_layout.addWidget(reference_btn, 0, 0)
        btn_grid_layout.addWidget(self.amount_lineEdit, 0, 2)
        #btn_grid_layout.addWidget(update_btn, 0, 1, 1, 1)
        top_level_layout.addLayout(btn_grid_layout)
        self.setLayout(top_level_layout)

    def item_sel_changed(self):
        self.sel_items = self.assets_qlist.selectedItems()

    def dep_rbox_changed(self, enabled):
        if self.mdl_rbox.isChecked():
            self.department_filter = "MDL"
        elif self.shd_rbox.isChecked():
            self.department_filter = "SHD"
        elif self.rig_rbox.isChecked():
            self.department_filter = "RIG"

        if enabled:
            self.update_qlist()

    def create_references(self):
        path_list = []

        for item in self.sel_items:
            for asset in self.asset_list:
                if item.text() in asset:
                    path_list.append(asset_parser.build_asset_path(asset_name=item.text(), department=self.department_filter))

        amount = int(self.amount_lineEdit.text())
        dresser_func(path_list=path_list, amount=amount)

    def filter_assets(self, department):
        filtered_assets = []

        for asset in self.asset_list:
            if asset[2][department]:
                filtered_assets.append(asset[0])

        return filtered_assets

    def update_qlist(self):
        self.assets_qlist.clear()

        asset_names = self.filter_assets(self.department_filter)

        self.assets_qlist.addItems(asset_names)
        self.assets_qlist.sortItems()


def dresser_func(path_list, amount):
    for path in path_list:
        namespace = path.split(".ma")[0].split("\\")[-1]
        for idx in range(amount):
            pmc.createReference(path, groupReference=True, namespace=namespace)
