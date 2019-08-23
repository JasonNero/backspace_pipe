import glob
import sys
import os
import subprocess

# only change these variables
arnold_bin_path = "C:/solidangle/mtoadeploy/2018/bin"
variance = 0.5
pixel_search_radius = 9
pixel_neighborhood_patch_radius = 3
temporal_range = 3

max_commands_per_file = 10

# # ALL
# aov_list = [
#     "diffuse_direct",
#     "diffuse_indirect",
#     "specular_direct",
#     "specular_indirect"
# ]

# # DIRECTS ONLY
# aov_list = [
#     "diffuse_direct",
#     "specular_direct",
# ]

# # INDIRECTS ONLY
# aov_list = [
#     "specular_indirect"
# ]

# SPEC ONLY
aov_list = [
    "specular_direct",
    "specular_indirect"
]

aov_list = [
    "diffuse_direct_Vending",
    "diffuse_indirect_Vending",
    "diffuse_indirect_Altar",
    "specular_indirect_Vending",
    "specular_indirect_Altar",
]


def denoise(file_list, aov_list):

    # bat_path = file_list[0].split(".")[-3] + "_deNoice.bat"

    denoise_folder = "\\".join(file_list[0].split("\\")[:-1]) + "\\_denoise"

    if not os.path.exists(denoise_folder):
        os.makedirs(denoise_folder)

    for number, file in enumerate(file_list):
        temporal_range_string = ""
        light_aov_string = ""

        if (number >= 3):
            temporal_range_string += "-i " + file_list[number - 1] + " " \
                + "-i " + file_list[number - 2] + " "\
                + "-i " + file_list[number - 3] + " "
        elif (number == 2):
            temporal_range_string += "-i " + file_list[number - 1] + " " \
                + "-i " + file_list[number - 2] + " "
        elif (number == 1):
            temporal_range_string += "-i " + file_list[number - 1] + " "
        elif (number == 0):
            pass

        for aov in aov_list:
            light_aov_string += "-aov " + aov + " "

        # out_file = file.split(".exr")[0] + "_denoice.exr"

        # Pfadgenerierung mit Unterordner "_denoice" und postfix ".denoice.exr"
        out_file = file.split("\\")[-1].split(".exr")[0] + ".denoise.exr"
        out_path = denoise_folder + "\\" + out_file

        # TODO: auslagern, praktisch als Wrapper
        line = arnold_bin_path + "/noice.exe " \
            + "-patchradius " + str(pixel_neighborhood_patch_radius) + " " \
            + "-searchradius " + str(pixel_search_radius) + " " \
            + "-variance " + str(variance) + " " \
            + light_aov_string + " " \
            + "-i " + file + " " \
            + temporal_range_string + " " \
            + "-output " + out_path + "\n"

        subprocess.call(line)


if __name__ == "__main__":
    print("\n####### DeNoice Batch Creator #######\n")
    print("You specified the following AOVs:")
    for aov in aov_list:
        print("....{aov}".format(aov=aov))

    print("\n")

    try:
        drop_file = sys.argv[1]
        file_prefix = drop_file.split(".")[-3]
        print("Using dropped file for file list creation")
        glob_path = file_prefix + ".*.exr"
        file_list = glob.glob(glob_path)
    except IndexError:
        print("Using current folder for file list creation")
        file_list = glob.glob("*.exr")


    print("\n######################################\n")
    # input("Press any key to start denoising...")

    file_list.sort()

    denoise(file_list=file_list, aov_list=aov_list)

    print("\n######################################\n")
    # input("Finished!")
