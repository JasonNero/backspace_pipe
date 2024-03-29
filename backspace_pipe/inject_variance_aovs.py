import glob
import re
import shutil
import sys

outputs_re = re.compile(r" outputs (\d+) \d+")


# aov_list = [
#     "diffuse_direct",
#     "diffuse_indirect",
#     "specular_direct",
#     "specular_indirect"
# ]

aov_list = [
    "diffuse_indirect",
    "specular_indirect"
]


def inject_aovs(file_list, aov_list):
    successful_injects = []

    for number, file_path in enumerate(file_list):
        print("\nNow processing {}/{}: {}".format(number + 1, len(file_list), file_path))
        with open(file_path) as f_old, open(file_path + ".tmp", "w") as f_new:
            aovs_written = 0
            for line in f_old:
                # UPDATE COUNT AND JUMP TO NEXT LINE
                if "outputs" in line:
                    match = outputs_re.match(line)
                    if not match:
                        print("ERROR - No regex match found, please check your Output Driver")
                        break
                    aov_count_old = int(match.group(1))
                    aov_count_new = aov_count_old + len(aov_list)
                    new_line = " outputs {count} 1 STRING\n".format(count=aov_count_new)
                    f_new.write(new_line)
                    continue

                # ALL ABOVE ARE MODIFICATIONS TO THE CURRENT LINE
                f_new.write(line)
                # ALL BELOW ARE APPENDICES TO BELOW THE CURRENT LINE

                # CHECK IF ALREADY RUN
                if "### variance aovs injected" in line:
                    print("WARNING - This file has already been injected. Skipping...")
                    break

                # ADD COMMENT
                if "### scene:" in line:
                    f_new.write("### variance aovs injected")

                # ADD VARIANCE AOVS
                for aov in aov_list:
                    if "{aov} RGB defaultArnoldFilter@gaussian_filter defaultArnoldDriver@driver_exr.RGBA".format(aov=aov) in line:
                        f_new.write('  "{aov} RGB defaultArnoldRenderOptions@variance_filter defaultArnoldDriver@driver_exr.RGBA {aov}_variance"\n'.format(aov=aov))
                        aovs_written += 1

            if aovs_written != len(aov_list):
                print("ERROR - Not all specified AOVs have been found and appended.")
                # break
            else:
                successful_injects.append(file_path)

    rename_tmp_files(successful_injects)


def rename_tmp_files(file_list):
    for number, file_path in enumerate(file_list):
        print("\nNow replacing {}/{}: {}".format(number + 1, len(file_list), file_path))
        shutil.copy(file_path + ".tmp", file_path)


if __name__ == "__main__":
    print("\n####### VARIANCE AOV INJECTOR #######\n")
    print("You specified the following AOVs:")
    for aov in aov_list:
        print("....{aov}".format(aov=aov))

    print("\n")

    try:
        drop_file = sys.argv[1]
        file_prefix = drop_file.split(".")[-3]
        print("Using dropped file for file list creation")
        glob_path = file_prefix + ".*.ass"
        file_list = glob.glob(glob_path)
    except IndexError:
        print("Using current folder for file list creation")
        file_list = glob.glob("*.ass")


    print("\n#####################################\n")
    input("Press any key to start the injection...")

    file_list.sort()

    inject_aovs(file_list=file_list, aov_list=aov_list)

    print("\n#####################################\n")
    input("Finished!")
