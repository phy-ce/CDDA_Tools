@echo off
cd /d "%~dp0"
title CDDA Recipe Helper
where py >nul 2>nul
if %errorlevel%==0 goto usepy
python -m cdda_recipes
goto done
:usepy
py -m cdda_recipes
:done
if errorlevel 1 pause
