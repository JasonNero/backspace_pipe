import os
import shutil
import sys

# fps_string = 'currentUnit -l centimeter -a degree -t film;'
# student_string = 'fileInfo "license" "education";'
dev_included = False


def bulk_check(root_path):
    non_unified = []

    print("Root Path: {}".format(root_path))

    for root, dirs, files in os.walk(root_path):

        # Skipping Development Folder for Speed
        if not dev_included:
            if "Development" in root or "development" in root:
                continue

        for file in files:
            if file.endswith(".ma"):
                file_path = root + "\\" + file
                if not is_unified(file_path):
                    non_unified.append(file_path)

    return non_unified


def is_unified(file_path):
    if os.path.isfile(file_path) and file_path.endswith(".ma"):
        print('Now checking: "%s"' % file_path)

        # Checking if scene doesnt fit
        with open(file_path, "r+") as maFile:
            newMaText = maFile.read(1024)
            if 'fileInfo "license" "student";' in newMaText or 'currentUnit -l centimeter -a degree -t pal;' in newMaText:
                print("Scene Not Unify!\n")
                return False
            else:
                print("Scene OK!\n")
                return True
    else:
        raise Exception("Not an Maya Ascii file!")


def bulk_unify(file_list):
    for file_path in file_list:
        unify(file_path)


def unify(file_path):
    if os.path.isfile(file_path) and file_path.endswith(".ma"):
        print('Now processing: "%s"' % file_path)

        # Checking if scene doesnt fit
        with open(file_path, "r+") as maFile:
            newMaText = maFile.read()

            # Creating backup
            print('Creating Backup...')
            try:
                bak_path = file_path + ".bak"
                shutil.copy(file_path, bak_path)
            except Exception as e:
                raise e

            newMaText = newMaText.replace(
                'fileInfo "license" "student";',
                'fileInfo "license" "education";'
            )

            newMaText = newMaText.replace(
                'currentUnit -l centimeter -a degree -t pal;',
                'currentUnit -l centimeter -a degree -t film;'
            )

            # Writing unified file
            print("Writing to file...\n")

            maFile.seek(0)
            maFile.write(newMaText)
            maFile.truncate()


if __name__ == "__main__":
    print("###     BULK_UNIFY_MA     ###")
    mode = input("'check' or 'unify' scenes: ")

    try:
        path = sys.argv[1]
    except IndexError:
        path = os.getcwd()

    if mode == "check":
        if os.path.isdir(path):
            print("Check everything inside of this folder: '{}'".format(path))
            input()

            non_unified_list = bulk_check(path)
            print("Non unified list:")

            for file in non_unified_list:
                print(file)

            print("\n")
        elif os.path.isfile(path):
            print("Check this file: '{}'".format(path))
            input()
            if is_unified(path):
                print("Scene OK!")
            else:
                print("Scene not unified!")
        else:
            path = os.getcwd()
            print("Check the current folder: '{}'?".format(path))
            input()

            non_unified_list = bulk_check(path)
            print("Non unified list:")

            for file in non_unified_list:
                print(file)

            print("\n")
    elif mode == "unify":
        if os.path.isdir(path):
            print("Unify everything inside of this folder: '{}'".format(path))
            input()

            non_unified_list = bulk_check(path)
            bulk_unify(non_unified_list)

        elif os.path.isfile(path):
            print("Unify this file: '{}'".format(path))
            input()
            if is_unified(path):
                print("Scene already OK!")
            else:
                print("Unify scene...")
                unify(path)
        else:
            path = os.getcwd()
            print("Unify the current folder: '{}'".format(path))
            input()

            non_unified_list = bulk_check(path)
            bulk_unify(non_unified_list)
    else:
        print("Wrong input!")

    input()
