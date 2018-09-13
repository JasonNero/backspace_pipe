@ECHO OFF

CLS
COLOR 06
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO    PLEASE MAKE SURE THAT YOU HAVE PYTHON 2.7
ECHO     INSTALLED BEFORE CONTINUING THIS SETUP
ECHO ...............................................
ECHO.
pause

CLS
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO             SETTING UP VIRTUALENV
ECHO ...............................................
ECHO.
ECHO CHECK VIRTUALENV:
pip install virtualenv
if ERRORLEVEL 0 GOTO PIPERR
IF NOT EXIST backspace_venv\Scripts\ virtualenv --python=c:\Python27\python.exe backspace_venv
ECHO.
ECHO CHECK REQUIREMENTS
backspace_venv\Scripts\pip install -r requirement.txt
ECHO.
pause

CLS
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO           INSTALLING BACKSPACE PIPE
ECHO ...............................................
ECHO.

py -2 pipe_installer.py
if ERRORLEVEL 0 GOTO EOF

python pipe_installer.py
if ERRORLEVEL 0 GOTO EOF

GOTO EOF


:PIPERR
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO              COULD NOT REACH PIP
ECHO             ABORTING INSTALLATION
ECHO ...............................................
ECHO.
GOTO EOF



:EOF
ECHO.
pause