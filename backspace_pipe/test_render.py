import subprocess
import sys

# resolution_str = "-r 1024 720 "
# resolution_str = "-r 960 540 "


def command_from_path(path):
    return "C:/solidangle/mtoadeploy/2018/bin/kick.exe -r 960 540 -dp -nokeypress -nocrashpopup -nostdin -set options.bucket_size 16 -set options.procedural_searchpath //am-ca-fs02/cg2/04_workflow -set options.texture_searchpath //am-ca-fs02/cg2/04_workflow -i {scene_path} -v 5 -l C:/solidangle/mtoadeploy/2018/shaders".format(scene_path=path)


if __name__ == "__main__":
    print("\n######### Quick Test Render #########\n")

    try:
        drop_file = sys.argv[1]
        print("Using dropped file")
        print(drop_file)
        input("Press any key to start rendering...")

        subprocess.call(command_from_path(drop_file))
    except IndexError:
        print("No file dropped!")

    print("\n######################################\n")
    input("Press any key to close window...")


# '"C:/solidangle/mtoadeploy/2018/bin/kick.exe" -dw -dp -nokeypress -nocrashpopup -nostdin -set options.procedural_searchpath //am-ca-fs02/cg2/04_workflow -set options.texture_searchpath //am-ca-fs02/cg2/04_workflow -i {scene_path} -v 5 -l C:/solidangle/mtoadeploy/2018/shaders'
# "C:/solidangle/mtoadeploy/2018/bin/kick.exe" -dw -dp -nokeypress -nocrashpopup -nostdin -set options.procedural_searchpath //am-ca-fs02/cg2/04_workflow -set options.texture_searchpath //am-ca-fs02/cg2/04_workflow -i D:/shot_020_LGT_021/shot_020_LGT_021_masterLayer.0060.ass -v 5 -l C:/solidangle/mtoadeploy/2018/shaders
