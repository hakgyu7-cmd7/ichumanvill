@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
cd /d "%~dp0"

rem ==== Settings: edit as you like ====
set LANG_CODE=ko
set CLIPS=5
set PRIVACY=private
rem ===================================

if "%~1"=="" (
  echo Drag and drop video file^(s^) onto this file.
  pause
  exit /b
)

:loop
if "%~1"=="" goto done
echo.
echo ===== %~nx1 =====
".venv\Scripts\python.exe" shorts.py "%~1" --lang %LANG_CODE% -n %CLIPS% --upload --privacy %PRIVACY%
shift
goto loop

:done
echo.
echo All done.
pause
