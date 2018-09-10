import os
import time
import shutil
import ctypes.wintypes

# wintype -> "My Documents"
CSIDL_PERSONAL = 5

# wintype -> get current, not default
SHGFP_TYPE_CURRENT = 0

pipe_path = os.getcwd().replace("\\", "\\\\")
venv_path = pipe_path + r"\\backspace_venv"
site_path = venv_path + r"\\Lib\\site-packages"
venv_activate_path = venv_path + r"\\Scripts\\activate.bat"

documents_path_buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documents_path_buf)

documents_path = documents_path_buf.value

usersetup_path = documents_path + "\\maya\\2018\\scripts\\usersetup.py"
shelf_path = documents_path + "\\maya\\2018\\prefs\\shelves\\shelf_Backspace.mel"

usersetup_content = '''
import sys
import site

sys.path.append('{pipe_path}')
site.addsitedir('{site_path}')
'''.format(pipe_path=pipe_path, site_path=site_path)


def usersetup():
    print("## Checking User Setup...")
    if os.path.exists(usersetup_path) and os.stat(usersetup_path).st_size != 0:
        print("# existing usersetup.py found!")

        with open(usersetup_path, "r") as f:
            file_content = f.read()

            setup_lines = usersetup_content.splitlines()

            for line in setup_lines:
                if line not in file_content:
                    file_content += "\n" + line

        with open(usersetup_path, "w") as f:
            f.write(file_content)
    else:
        print("# usersetup.py not found or empty.")
        with open(usersetup_path, "a") as f:
            f.write(usersetup_content)

def shelves():
    print("## Installing Backspace Shelf...")
    if os.path.exists(shelf_path):
        print("# Replacing Backspace Shelf")
        shutil.copy(pipe_path + "\\shelves\\shelf_Backspace.mel", shelf_path)
    else:
        shutil.copy(pipe_path + "\\shelves\\shelf_Backspace.mel", shelf_path)



if __name__ == "__main__":
    print("##################################")
    print("### Installing Backspace Pipe... ")
    usersetup()
    shelves()
    print("### Installation Complete! ")
    print("##################################")
    time.sleep(1)
