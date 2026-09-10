@echo off
rem OpenViking disaster-recovery backup: data -> D:\openviking-backup\repo -> GitHub private repo
rem vectordb/ and temp/ intentionally excluded: rebuildable via local bge-m3
rem Guard: aborts (exit 2) before mirroring when the source holds a large-shrink share of the
rem backup (possible source loss). The backup is left untouched; a line is logged.
rem Confirm intent, then override with: set OV_BACKUP_FORCE=1
rem Overridable for tests/reconfig: OV_SRC, OV_DST, OV_LOG
setlocal

if not defined OV_SRC set "OV_SRC=%USERPROFILE%\.openviking\data\viking\default"
if not defined OV_DST set "OV_DST=D:\openviking-backup\repo"
if not defined OV_LOG set "OV_LOG=%~dp0abort.log"
set "SRC=%OV_SRC%"
set "DST=%OV_DST%"

if not exist "%SRC%\user" (
  echo [OV-BACKUP] source missing: %SRC%\user - aborting
  exit /b 1
)

rem --- large-deletion guard: source file count vs backup file count ---
set SRC_N=0
set DST_N=0
for /f %%C in ('powershell -NoProfile -Command "@((Get-ChildItem -Path $env:SRC -Recurse -File -Force -ErrorAction SilentlyContinue)).Count"') do set SRC_N=%%C
for /f %%C in ('powershell -NoProfile -Command "@((Get-ChildItem -Path $env:DST -Recurse -File -Force -ErrorAction SilentlyContinue)).Count"') do set DST_N=%%C

set /a OV_MIN=DST_N*70/100
if %DST_N% LSS 100 goto :mirror
if %SRC_N% GEQ %OV_MIN% goto :mirror
if "%OV_BACKUP_FORCE%"=="1" goto :mirror
echo [OV-BACKUP] ABORT: source has %SRC_N% files vs backup %DST_N% - possible source loss
echo [OV-BACKUP] backup left untouched; confirm intent, then rerun with OV_BACKUP_FORCE=1
echo [%date% %time%] ABORT src=%SRC_N% dst=%DST_N% force=0 >> "%OV_LOG%"
exit /b 2

:mirror
robocopy "%SRC%\user" "%DST%\user" /MIR /NFL /NDL /NJH /NJS >nul
robocopy "%SRC%\resources" "%DST%\resources" /MIR /NFL /NDL /NJH /NJS >nul

cd /d "%DST%"
git add -A
git diff --cached --quiet && exit /b 0
git commit -m "backup: daily snapshot %date% %time%" >nul
git push origin main
if errorlevel 1 (
  echo [OV-BACKUP] push failed - local commit kept, will retry next run
  exit /b 1
)
echo [OV-BACKUP] OK
exit /b 0
