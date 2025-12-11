@echo off
title Instalador - Splynx Tecnicos cada 5 minutos (EXE)
color 0A

echo ===============================================
echo    Instalando tarea automatica cada 5 minutos
echo    Splynx_Tecnicos_Calendar (EXE)
echo ===============================================
echo.

REM === Ruta del BAT que ejecuta el EXE ===
set "SCRIPT_DIR=%~dp0"
set "RUNNER=%SCRIPT_DIR%run_tecnicos_calendar.bat"

echo Usando archivo: %RUNNER%
echo.

REM === Nombre de la tarea en Windows ===
set "TASK_NAME=Splynx_Tecnicos_Calendar"

REM === Si ya existe, la borramos para recrearla limpia ===
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo La tarea ya existe. Eliminando...
    schtasks /Delete /TN "%TASK_NAME%" /F >nul
)

echo Creando nueva tarea cada 5 minutos...
echo.

schtasks /Create ^
 /SC MINUTE ^
 /MO 5 ^
 /TN "%TASK_NAME%" ^
 /TR "%RUNNER%" ^
 /RL HIGHEST ^
 /F

if %ERRORLEVEL%==0 (
    echo ===============================================
    echo  ✔ Tarea instalada correctamente
    echo  ✔ Se ejecutara cada 5 minutos
    echo ===============================================
) else (
    echo ===============================================
    echo  ✖ ERROR al crear la tarea
    echo ===============================================
)

echo.
pause
exit
