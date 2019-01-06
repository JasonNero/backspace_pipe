import pymel.core as pmc
from backspace_pipe import logging_control

logger = logging_control.get_logger()


MODE_BBOX = 0
MDOE_OBJ_BBOX = 1
MODE_POLYWIRE = 2
MODE_WIRE = 3
MODE_POINTCLOUD = 4
MODE_SHADED_POLYWIRE = 5
MODE_SHADED = 6

def set_all_draw_mode(draw_mode):
	standins = pmc.ls(type="aiStandIn")

	for standin in standins:
		logger.debug("Now processing: {}".format(standin))
		standin.mode.set(draw_mode)
