import os
import time
import shutil

pipe_path = os.getcwd().replace("\\", "\\\\")
venv_path = pipe_path + r"\\backspace_venv\\Lib\\site-packages"

usersetup_path = os.path.expanduser(r"~\\Documents\\maya\\2018\\scripts\\usersetup.py")
shelf_path = os.path.expanduser(r"~\\Documents\\maya\\2018\\prefs\\shelves\\shelf_Backspace.mel")

usersetup_content = '''
import sys
import site

sys.path.append('{pipe_path}')
site.addsitedir('{venv_path}')
'''.format(pipe_path=pipe_path, venv_path=venv_path)

def usersetup():
	print("## Checking User Setup...")
	if os.path.exists(usersetup_path) and os.stat(usersetup_path).st_size != 0:
		print("# existing usersetup.py found!")

		with open(usersetup_path, "r") as f:
			file_content = f.read()

			setup_lines = usersetup_content.splitlines()

			for line in setup_lines:
				if not line in file_content:
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
	print("\n##################################")
	print("### Installing Backspace Pipe... ")
	usersetup()
	shelves()
	print("### Installation Complete! ")
	print("##################################")
	time.sleep(5)