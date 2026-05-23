@echo off
chcp 65001 >nul
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%split_drums.py"
set "SELECTOR_SCRIPT=%SCRIPT_DIR%select_song.ps1"
set "SOURCE_DIR=%SCRIPT_DIR%original_songs"
set "MODEL=htdemucs_ft"
if not defined CONDA_PATH set "CONDA_PATH=%USERPROFILE%\anaconda3"
if not defined CONDA_ENV set "CONDA_ENV=newyolov5"

echo.
echo ========================================================
echo Drum Splitter
echo ========================================================
echo.
echo Starting Conda environment: %CONDA_ENV%...
call "%CONDA_PATH%\Scripts\activate.bat" %CONDA_ENV%
if errorlevel 1 (
    echo Failed to activate Conda environment, trying direct Python path...
    set "PYTHON_EXE=%CONDA_PATH%\envs\%CONDA_ENV%\python.exe"
) else (
    echo Conda environment activated.
    set "PYTHON_EXE=python"
)

echo.
echo Source directory: %SOURCE_DIR%
echo Default model: %MODEL%
echo.

if not exist "%SOURCE_DIR%" (
    echo Source directory not found: "%SOURCE_DIR%"
    echo Please verify that the folder exists.
    pause
    exit /b 1
)

if not exist "%PYTHON_SCRIPT%" (
    echo Python script not found: "%PYTHON_SCRIPT%"
    pause
    exit /b 1
)

if not exist "%SELECTOR_SCRIPT%" (
    echo Song selector script not found: "%SELECTOR_SCRIPT%"
    pause
    exit /b 1
)

call :select_mode
if errorlevel 1 (
    echo.
    echo Operation cancelled.
    pause
    exit /b 0
)

call :select_song
if errorlevel 1 (
    echo.
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo ========================================================
echo Ready to process
echo ========================================================
echo Song: %SELECTED_NAME%
echo Mode: %MODE_LABEL%
echo Model: %MODEL%
echo.

set "EXTRA_ARGS="
if "%KEEP_DRUMS%"=="1" (
    set "EXTRA_ARGS=--keep-drums"
)

"%PYTHON_EXE%" "%PYTHON_SCRIPT%" "%SELECTED_FILE%" --model %MODEL% %EXTRA_ARGS%

if errorlevel 1 (
    echo.
    echo Processing failed: %SELECTED_NAME%
) else (
    echo.
    echo Processing complete: %SELECTED_NAME%
)

echo.
echo ========================================================
echo Done
echo ========================================================
pause
exit /b 0

:select_mode
echo ========================================================
echo Select output mode
echo ========================================================
echo [1] Keep drums only ^(drums.wav^)
echo [2] Remove drums ^(no_drums.wav^)
echo [Q] Cancel
echo.
choice /c 12Q /n /m "Press 1, 2, or Q: "

if errorlevel 3 exit /b 1
if errorlevel 2 (
    set "KEEP_DRUMS=0"
    set "MODE_LABEL=Remove drums (no_drums.wav)"
    exit /b 0
)

set "KEEP_DRUMS=1"
set "MODE_LABEL=Keep drums only (drums.wav)"
exit /b 0

:select_song
set "SELECTED_FILE="
set "SELECTED_NAME="

for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%SELECTOR_SCRIPT%" -SourceDir "%SOURCE_DIR%" 2^>nul`) do (
    if not defined SELECTED_FILE (
        set "SELECTED_FILE=%%~fI"
    )
)

set "SELECTOR_EXIT=%ERRORLEVEL%"
if not "%SELECTOR_EXIT%"=="0" (
    exit /b 1
)

if not defined SELECTED_FILE (
    exit /b 1
)

if not exist "%SELECTED_FILE%" (
    echo Song selection failed.
    exit /b 1
)

for %%I in ("%SELECTED_FILE%") do (
    set "SELECTED_NAME=%%~nxI"
)

exit /b 0
