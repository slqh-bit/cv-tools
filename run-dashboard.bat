@echo off
REM ---------------------------------------------------------------------
REM  cv-tools web dashboard.
REM
REM  Double-click to launch. The browser opens by itself a few seconds
REM  later, once the server is answering.
REM
REM  Bound to 127.0.0.1 deliberately: started plainly, Streamlit listens on
REM  every interface, which puts a tool that ingests evidence images on the
REM  network. To share it on purpose, change the address below to 0.0.0.0
REM  and set CVTOOLS_PASSWORD first so the password gate is active.
REM
REM  Close this window, or press Ctrl+C in it, to stop the server.
REM ---------------------------------------------------------------------
setlocal
pushd "%~dp0"

set "PY=%~dp0.venv\Scripts\python.exe"
set "PORT=8501"

if not exist "%PY%" (
    echo.
    echo  The project environment is missing:
    echo    %PY%
    echo.
    echo  Create it from this folder with:
    echo    python -m venv .venv
    echo    .venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dashboard.txt
    echo.
    pause
    popd
    exit /b 1
)

echo.
echo  Starting the cv-tools dashboard on http://localhost:%PORT%
echo  Close this window to stop it.
echo.

REM Open the browser a few seconds from now, while the server starts here.
REM headless keeps Streamlit from asking for an email address on first run.
start "" /b cmd /c "timeout /t 5 /nobreak >nul & start "" http://localhost:%PORT%"

"%PY%" -m streamlit run src\dashboard.py ^
    --server.address=127.0.0.1 ^
    --server.port=%PORT% ^
    --server.headless=true ^
    --browser.gatherUsageStats=false

if errorlevel 1 (
    echo.
    echo  The dashboard exited with an error - the message is above.
    echo  If it says the port is in use, another copy is already running.
    pause
)

popd
