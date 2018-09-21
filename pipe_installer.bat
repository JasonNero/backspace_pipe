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

IF NOT EXIST c:\\Python27\\python.exe GOTO 


CLS
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO             SETTING UP VIRTUALENV
ECHO ...............................................
ECHO.
ECHO CHECK VIRTUALENV INSTALLATION:

c:\\Python27\\python.exe -m pip install virtualenv
if ERRORLEVEL 0 GOTO VENVSETUP ELSE GOTO PIPERR

:VENVSETUP
IF NOT EXIST backspace_venv\\Scripts\\ 
(
	virtualenv --python=c:\\Python27\\python.exe backspace_venv
) ELSE (
	ECHO VENV ALREADY SETUP
)

ECHO.
ECHO CHECK REQUIREMENTS:
backspace_venv\\Scripts\\pip install -r requirement.txt
ECHO.
pause

CLS
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO           INSTALLING BACKSPACE PIPE
ECHO ...............................................
ECHO.


c:\\Python27\\python.exe pipe_installer.py
if ERRORLEVEL 0 GOTO EOF ELSE GOTO PYERR


:PYERR
ECHO.
ECHO ............... BACKSPACE PIPE ................
ECHO            COULD NOT FIND PYTHON 2.7
ECHO          PLEASE INSTALL TO C:\Python27
ECHO ...............................................
ECHO.
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