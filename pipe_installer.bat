@ECHO OFF

CLS
:MENU
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO PLEASE MAKE SURE THAT YOU HAVE PYTHON 2.7 INSTALLED
ECHO.
ECHO IS THIS YOUR FIRST INSTALLATION OF BACKSPACE_PIPE?
ECHO ...............................................
ECHO.
ECHO 1 - YES
ECHO 2 - NOT
ECHO 3 - EXIT
ECHO.
SET /P M=INPUT:
CLS
IF %M%==1 GOTO FIRST
IF %M%==2 GOTO REST
IF %M%==3 GOTO EOF


:FIRST
CLS
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO             SETTING UP VIRTUALENV
ECHO ...............................................
ECHO.
pip install virtualenv
virtualenv --python=c:\Python27\python.exe backspace_venv
backspace_venv\Scripts\pip install -r requirement.txt
GOTO REST


:REST
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

:EOF
pause