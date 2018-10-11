import pymel.core as pmc

def export_obj(force, object):
	
	scene_file = pmc.sceneName()
	scene_name = scene_file.splitext()[0].split("/")[-1]
	export_path = scene_file.parent.parent.parent / "Export"
	export_file = export_path / scene_name + "__" + object.s


	pmc.select(object)
	pmc.exportSelected(path, force=True, preserveReferences=True, type="OBJExport")
	


def export_fbx():
	pass