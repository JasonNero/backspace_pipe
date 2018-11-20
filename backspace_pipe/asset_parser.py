import os
import pymel.core as pmc

#setpieces_path = pmc.Path(__file__).splitdrive()[0] / "04_workflow" / "scenes" / "assets" / "setpieces" / ""
setpieces_path = pmc.Path("M:/04_workflow/scenes/assets/setpieces")


def parse():
    asset_list = []

    asset_folders = os.listdir(setpieces_path)

    for asset_dir in asset_folders:
        asset_status_dict = {"DEV": False, "MDL": False, "RIG": False, "SHD": False, "LGT": False}
        asset_maya_dir = setpieces_path / asset_dir / "Maya"

        if os.path.isdir(asset_maya_dir):
            for department in ["MDL", "RIG", "SHD", "LGT"]:
                asset_status_dict[department] = os.path.isfile(asset_maya_dir / "{asset_name}_{dep}_REF.ma".format(asset_name=asset_dir, dep=department))

            # if Development folder is empty
            if [f for f in os.listdir(asset_maya_dir / "Development") if not f.startswith('.')] == []:
                asset_status_dict["DEV"] = False
            else:
                asset_status_dict["DEV"] = True

            # asset_status_dict[department] = os.path.isfile(asset_maya_dir / "Development" / "{asset_name}_{dep}_REF.ma".format(asset_name=asset_dir, dep=department))

            asset_list.append([asset_dir, os.path.normpath(setpieces_path / asset_dir), asset_status_dict])

    return asset_list


def build_asset_path(asset_name, department):
    asset_path = os.path.normpath(setpieces_path / asset_name / "Maya" / "{asset_name}_{dep}_REF.ma".format(asset_name=asset_name, dep=department))
    return asset_path
