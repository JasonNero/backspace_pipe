import os
import time

scripts_path = os.getcwd().replace("\\", "\\\\")
venv_path = scripts_path + r"\\backspace_venv\\Lib\\site-packages"
usersetup_path = os.path.expanduser(r"~\\Documents\\maya\\2018\\scripts\\usersetup.py")

usersetup_content = '''
import sys
import site

sys.path.append('{scripts_path}')
site.addsitedir('{venv_path}')
'''.format(scripts_path=scripts_path, venv_path=venv_path)

def usersetup():
	print("\n##################################")
	print("## Installing Backspace Pipe... ")

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

	print("## Installation Complete! ")
	print("##################################")
	time.sleep(5)

if __name__ == "__main__":
	usersetup()