@echo off
REM ---------------------------------------------------------------------
REM  cv-tools desktop app.
REM
REM  Double-click to launch, or drop an image onto this file to open it
REM  straight away.
REM
REM  It calls the project venv by full path on purpose: a bare "python" on
REM  this machine resolves to another project's environment, which has no
REM  OpenCV in it.
REM ---------------------------------------------------------------------
setlocal
pushd "%~dp0"

set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo.
    echo  The project environment is missing:
    echo    %PY%
    echo.
    echo  Create it from this folder with:
    echo    python -m venv .venv
    echo    .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    popd
    exit /b 1
)

REM %* passes through anything dropped on the icon or typed after the name
"%PY%" -m cv_tools.gui %*

REM Only pause on a failure, so a normal close does not leave a window behind
if errorlevel 1 (
    echo.
    echo  The app exited with an error - the message is above.
    pause
)

popd
